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

from ...range_aggregate_scheme import RangeAggregateScheme
from ...range_aggregate_querier import (
    RangeAggregateQuerier,
    ResolveDone,
)
from ...table import Table
from ...domain import Domain
from ...range_query import RangeQuery

from ....util.math import log2_ceil

from typing import Dict, Iterable, List, Tuple
from dataclasses import dataclass
from tqdm import trange

import math


class MinimumASTable(
    RangeAggregateScheme[Dict[Tuple[int, int], int], Tuple[int, int], int]
):
    """
    Implements the one-dimensional minimum technique for using the [AS87]
    interval selection technique.
    """

    def setup(self, table: Table) -> Dict[Tuple[int, int], int]:
        as_table_ds: Dict[Tuple[int, int], int] = {}

        ending_power_of_2 = log2_ceil(table.domain.size())
        table_points = list(
            table.iterate_over_unique_domain_points(
                lambda lst: min(lst) if len(lst) > 0 else 0
            )
        )
        for power in trange(ending_power_of_2 + 1, leave=False):
            range_size = 2**power
            num_segments = math.ceil(table.domain.size() / range_size)

            for segment_index in trange(num_segments, leave=False):
                start = segment_index * range_size
                end = min(start + range_size, table.domain.size())
                halfway = min(start + int(range_size / 2), end)

                ds1 = self.__running_minimum(
                    table_points, power, reversed(range(start, halfway))
                )
                ds2 = self.__running_minimum(table_points, power, range(halfway, end))
                as_table_ds = {**as_table_ds, **ds1, **ds2}

        return as_table_ds

    def generate_querier(
        self, domain: Domain, query: RangeQuery
    ) -> MinimumASTableQuerier:
        return MinimumASTableQuerier(domain=domain, initial_query=query)

    def __running_minimum(
        self, table_points: List[int], level: int, iterator: Iterable[int]
    ) -> Dict[Tuple[int, int], int]:
        as_table_ds = {}

        current_minimum = None
        for i in iterator:
            value = table_points[i]
            if current_minimum is None or value < current_minimum:
                current_minimum = value
            as_table_ds[(level, i)] = current_minimum

        return as_table_ds


@dataclass(frozen=True)
class MinimumASTableQuerier(RangeAggregateQuerier[Tuple[int, int], int]):
    """
    Associated querier for the :class:`MinimumASTable` scheme.
    """

    domain: Domain
    initial_query: RangeQuery

    def query(self) -> List[Tuple[int, int]]:
        start = self.initial_query.start
        end = self.initial_query.end - 1
        level = (start ^ end).bit_length()
        return list({(level, start), (level, end)})

    def resolve(self, responses: List[int]) -> ResolveDone:
        return ResolveDone(min(responses))
