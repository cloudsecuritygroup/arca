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
from ....util.math import log2_ceil, log2_floor

from typing import Dict, List, Tuple
from decimal import Decimal
from tqdm import trange

import math


class MedianAlphaApprox(
    RangeAggregateScheme[Dict[Tuple[int, int], List[int]], Tuple[int, int], List[int]]
):
    r"""
    Implements the alpha-approximate median algorithm from [BKMT05].

    The BKMT algorithm relies on the following observation about the
    median: given a sufficiently long query interval, the effects of the
    elements in a small prefix and suffix of the interval are minimal on
    the median and can be ignored. Thus, we can avoid precomputing
    some sub-medians while still achieving the desired approximation.

    :class:`MedianAlphaApproximate` must be instantiated with a particular
    choice of :math:`0 < \alpha < 1`, which affects the accuracy of the
    approximation. [BKMT05] and [EMT22] explain this parameter in more
    detail. Generally, the accuracy of the approximation increases as
    :math:`\alpha` tends to 1.
    """

    __slots__ = ["alpha"]

    def __init__(self, alpha: float):
        if not 0 < alpha < 1:
            raise ValueError("alpha must be 0 < alpha < 1")
        #: The approximation factor for the scheme.
        self.alpha = alpha

    def setup(self, table: Table) -> Dict[Tuple[int, int], List[int]]:
        median_ds = {}
        domain_size = table.domain.size()
        k = log2_ceil(domain_size)
        max_p = math.ceil((2 * (1 + self.alpha)) / (1 - self.alpha))
        for level in trange(1, k + 1, leave=False):
            block_size = 2 ** (k - level)
            num_blocks = math.ceil(domain_size / block_size)

            for j in trange(1, num_blocks + 1, leave=False):
                medians: List[int] = []
                for p in trange(1, max_p + 1, leave=False):
                    start = min((j - 1) * block_size, table.domain.end - 1)
                    end = min(start + (p * block_size), table.domain.end)
                    entries = table.filter_range(RangeQuery(start=start, end=end))
                    median = self.__compute_median(entries)
                    medians.append(median)
                median_ds[(level, j)] = medians

        return median_ds

    def generate_querier(
        self, domain: Domain, query: RangeQuery
    ) -> MedianAlphaApproxQuerier:
        return MedianAlphaApproxQuerier(
            domain=domain, initial_query=query, alpha=self.alpha
        )

    def __compute_median(self, unioned_list: List[int]) -> int:
        if len(unioned_list) <= 0:
            return 0
        sorted_list = list(sorted(unioned_list))
        midpoint = math.ceil(len(sorted_list) / 2) - 1
        return sorted_list[midpoint]


class MedianAlphaApproxQuerier(RangeAggregateQuerier[Tuple[int, int], List[int]]):
    """
    Associated querier for the :class:`MedianAlphaApproximate` scheme.
    """

    def __init__(self, domain: Domain, initial_query: RangeQuery, alpha: float):
        self.domain = domain
        self.initial_query = initial_query
        self.alpha = alpha
        self.p = -1  # temporary sentinel value

    def query(self) -> List[Tuple[int, int]]:
        max_blocks = 2 * math.ceil((2 * self.alpha) / (1 - self.alpha))

        maximum_level = log2_ceil(self.domain.size())
        initial_level = maximum_level - log2_floor(self.initial_query.length()) + 1

        level_offset = log2_floor(max_blocks + 2) - 2
        level = min(initial_level + level_offset, maximum_level)

        block_size = 2 ** (maximum_level - level)
        start_block_index = math.ceil(self.initial_query.start / block_size) + 1
        end_block_index = math.floor(self.initial_query.end / block_size)

        self.p = end_block_index - start_block_index
        return [(level, start_block_index)]

    def resolve(self, responses: List[List[int]]) -> ResolveDone:
        return ResolveDone(Decimal(responses[0][self.p]))
