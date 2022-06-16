##
## Copyright 2022 Zachary Espiritu
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##

from __future__ import annotations

from .minimum_sparse_table import MinimumSparseTable
from ...range_aggregate_scheme import RangeAggregateScheme
from ...range_aggregate_querier import (
    RangeAggregateQuerier,
    ResolveDone,
)
from ...table import Table
from ...domain import Domain
from ...range_query import RangeQuery
from ....util.math import log2_ceil


from typing import Dict, List, Tuple

import math
import itertools
import enum


# Sentinel value used to populate the third element of the tuples used to
# key the dictionary in the MinimumLinearEMT scheme (the third element of
# the tuples are not used for the lookup tables; the third element is only
# used for the sparse table elements).
LOOKUP_THIRD_ELEMENT = 0


class MinimumLinearEMTTableID(enum.IntEnum):
    """
    Internal class assigning identifers to each of the data structures used
    in the :class:`MinimumLinearEMT` scheme.
    """

    #: ID for the left-sided lookup table.
    LOOKUP_LEFT = 0

    #: ID for the right-sided lookup table.
    LOOKUP_RIGHT = 1

    #: ID for the sparse table.
    SPARSE_TABLE = 2


class MinimumLinearEMT(
    RangeAggregateScheme[Dict[Tuple[int, int, int], int], Tuple[int, int, int], int]
):
    """
    Implements the one-dimensional sparse table technique for range minimum
    queries from [EMT22]. This scheme allows for asymptotically linear
    storage in exchange for a limitation on the query size.
    """

    def __init__(self) -> None:
        self.minimum_sparse_table_scheme = MinimumSparseTable()

    @staticmethod
    def compute_block_size(domain_size: int) -> int:
        return max(log2_ceil(domain_size), 1)

    def setup(self, table: Table) -> Dict[Tuple[int, int, int], int]:
        block_size = MinimumLinearEMT.compute_block_size(table.domain.size())
        num_blocks = math.ceil(table.domain.size() / block_size)

        # Divide the domain into blocks of size `block_size`:
        blocks = [
            table.filter_range(
                RangeQuery(
                    start=block_index * block_size,
                    end=min((block_index + 1) * block_size, table.domain.size()),
                )
            )
            for block_index in range(num_blocks)
        ]

        block_minimums = map(lambda block: min(block) if len(block) > 0 else 0, blocks)

        # Make the sparse table over the block_minimums:
        block_minimum_table = Table.make(list(enumerate(block_minimums)))
        sparse_table = self.minimum_sparse_table_scheme.setup(block_minimum_table)

        # Convert everything to a dict:
        combined_structure: Dict[Tuple[int, int, int], int] = {}
        for key, value in sparse_table.items():
            combined_structure[(MinimumLinearEMTTableID.SPARSE_TABLE, *key)] = value

        # Make the lookup tables:
        lookup_left = [0] * table.domain.size()
        lookup_right = [0] * table.domain.size()
        for block_index, block in enumerate(blocks):
            start = block_index * block_size
            end = min(start + block_size, table.domain.size())

            # Fixed LEFT, moving RIGHT (and vice versa):
            lookup_left[start:end] = itertools.accumulate(block, min)
            lookup_right[start:end] = list(
                reversed(list(itertools.accumulate(reversed(block), min)))
            )

        lookup_tables = [
            (MinimumLinearEMTTableID.LOOKUP_LEFT, lookup_left),
            (MinimumLinearEMTTableID.LOOKUP_RIGHT, lookup_right),
        ]
        for lookup_table_id, lookup_table in lookup_tables:
            for index, value in enumerate(lookup_table):
                combined_structure[
                    (lookup_table_id, index, LOOKUP_THIRD_ELEMENT)
                ] = value

        return combined_structure

    def generate_querier(
        self, domain: Domain, query: RangeQuery
    ) -> MinimumLinearEMTQuerier:
        return MinimumLinearEMTQuerier(
            domain=domain,
            initial_query=query,
            minimum_sparse_table_scheme=self.minimum_sparse_table_scheme,
        )


class MinimumLinearEMTQuerier(RangeAggregateQuerier[Tuple[int, int, int], int]):
    """
    Associated querier for the :class:`MinimumSparseTable` scheme.
    """

    def __init__(
        self,
        domain: Domain,
        initial_query: RangeQuery,
        minimum_sparse_table_scheme: MinimumSparseTable,
    ):
        self.domain = domain
        self.initial_query = initial_query
        self.minimum_sparse_table_scheme = minimum_sparse_table_scheme

    def query(self) -> List[Tuple[int, int, int]]:
        queries: List[Tuple[int, int, int]] = [
            (
                MinimumLinearEMTTableID.LOOKUP_RIGHT,
                self.initial_query.start,
                LOOKUP_THIRD_ELEMENT,
            ),
            (
                MinimumLinearEMTTableID.LOOKUP_LEFT,
                self.initial_query.end - 1,
                LOOKUP_THIRD_ELEMENT,
            ),
        ]

        block_size = MinimumLinearEMT.compute_block_size(self.domain.size())

        start_block_index = math.floor(self.initial_query.start / block_size)
        end_block_index = math.floor(self.initial_query.end / block_size)

        # Check if sparse table is necessary:
        block_span_length = end_block_index - start_block_index
        if block_span_length == 0:
            raise ValueError("query is too small")
        # if block_span_length == 1, then do nothing else.
        elif block_span_length > 1:
            sparse_table_range_start = start_block_index + 1
            sparse_table_range_end = end_block_index
            sparse_table_querier = self.minimum_sparse_table_scheme.generate_querier(
                domain=self.domain,
                query=RangeQuery(
                    start=sparse_table_range_start, end=sparse_table_range_end
                ),
            )
            queries += list(
                map(
                    lambda query: (MinimumLinearEMTTableID.SPARSE_TABLE, *query),
                    sparse_table_querier.query(),
                )
            )

        return queries

    def resolve(self, responses: List[int]) -> ResolveDone:
        if len(responses) <= 0:
            raise ValueError("responses cannot be empty")
        return ResolveDone(min(responses))
