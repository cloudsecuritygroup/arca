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

from typing import Dict, List
from tqdm import tqdm, trange


class SumPrefix(RangeAggregateScheme[Dict[int, int], int, int]):
    """
    Implements one-dimensional prefix sums.
    """

    def setup(self, table: Table) -> Dict[int, int]:
        running_sum = 0
        prefix_mapping = {}
        for domain_value in trange(table.domain.start, table.domain.end, leave=True):
            sum_at_value = sum(table.filter(domain_value))
            running_sum += sum_at_value
            prefix_mapping[domain_value] = running_sum
        return prefix_mapping

    def generate_querier(self, domain: Domain, query: RangeQuery) -> SumPrefixQuerier:
        return SumPrefixQuerier(domain=domain, initial_query=query)


class SumPrefixQuerier(RangeAggregateQuerier[int, int]):
    """
    Associated querier for the :class:`SumPrefix` scheme.
    """

    def __init__(self, domain: Domain, initial_query: RangeQuery):
        self.domain = domain
        self.initial_query = initial_query

    def query(self) -> List[int]:
        start = self.initial_query.start - 1
        end = self.initial_query.end - 1

        queries = []
        if start >= self.domain.start:
            queries.append(start)
        if end >= self.domain.start:
            queries.append(end)
        return queries

    def resolve(self, responses: List[int]) -> ResolveDone:
        original_queries = self.query()
        if len(original_queries) > 1:
            return ResolveDone(responses[1] - responses[0])
        else:
            return ResolveDone(responses[0])
