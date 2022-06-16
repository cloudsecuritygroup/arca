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

from typing import Deque, Dict, Iterable, Iterator, List, Tuple
from dataclasses import dataclass

import collections


class MinimumSparseTable(
    RangeAggregateScheme[Dict[Tuple[int, int], int], Tuple[int, int], int]
):
    """
    Implements the one-dimensional sparse table technique for range minimum
    queries from [BFPSS05].
    """

    def setup(self, table: Table) -> Dict[Tuple[int, int], int]:
        ending_power_of_2 = log2_ceil(table.domain.size())
        sparse_table_ds = {}
        table_points = list(
            table.iterate_over_unique_domain_points(
                lambda lst: min(lst) if len(lst) > 0 else 0
            )
        )
        for power in range(ending_power_of_2):
            range_size = 2**power
            for index, minimum in enumerate(
                self.__sliding_window_minimum(
                    range_size,
                    table_points,
                )
            ):
                sparse_table_ds[(power, index)] = minimum

        return sparse_table_ds

    def generate_querier(
        self, domain: Domain, query: RangeQuery
    ) -> MinimumSparseTableQuerier:
        return MinimumSparseTableQuerier(domain=domain, initial_query=query)

    def __sliding_window_minimum(
        self, window_size: int, lst: Iterable[int]
    ) -> Iterator[int]:
        """
        A iterator which takes the size of the window, `window_size`, and
        an iterable, `lst`. Then returns an iterator such that the ith element
        yielded is equal to min(list(lst)[max(i - window_size + 1, 0):i+1]).

        Each yield takes amortized O(1) time, and overall the generator
        requires O(window_size) space.

        Source (licensed under the MIT License):
        https://github.com/keegancsmith/Sliding-Window-Minimum/blob/master/sliding_window_minimum.py

        :param window_size: the size of the window
        :param lst: an iterable
        :return: an iterator
        """
        window: Deque[Tuple[int, int]] = collections.deque()
        for i, x in enumerate(lst):
            while window and window[-1][0] >= x:
                window.pop()
            window.append((x, i))
            while window[0][1] <= i - window_size:
                window.popleft()
            yield window[0][0]


@dataclass(frozen=True)
class MinimumSparseTableQuerier(RangeAggregateQuerier[Tuple[int, int], int]):
    """
    Associated querier for the :class:`MinimumSparseTable` scheme.
    """

    domain: Domain
    initial_query: RangeQuery

    def query(self) -> List[Tuple[int, int]]:
        # The "power" is the "level of the table" that we should query. It
        # corresponds to the size of the windows that were used to populate
        # the table; specifically, the windows are of size 2**power.
        power = log2_floor(self.initial_query.end - self.initial_query.start)
        window_size = 2**power

        # A (not-so-brief) example to help understand how these table indexes
        # are computed...
        #
        # Suppose we query the range [0, 6) on the following toy array:
        #
        #   [0, 1, 2, 3, 4, 5, 6]
        #
        # The range [0, 6) results in us needed to access the table level
        # corresponding to the windows of size
        #
        #   2**power = 2**floor(log2(6-0)) = 2**2
        #
        # where the start of the first window lines up with domain point 0
        # and the end of the second window lines up with domain point 5 (since
        # we've defined `RangeQuery`s to be exclusive of the endpoint).
        #
        # Thus, we need to access the following two windows:
        #
        #      [0, 1, 2, 3, 4, 5, 6]
        #   A:  |________|
        #   B:        |________|
        #
        # For range_1_index, we want the window that corresponds to Window A.
        # Recall that __sliding_window_minimum (used to generate the table in
        # `setup`) uses what we call "left-hanging" windows (i.e. the initial
        # elements of the sliding window iterator have the window "hanging
        # off" of the left-side of the array. Thus, in this example, we should
        # query index 3, since that corresponds to the window of size 2**2
        # whose left-most point lines up with domain point 0:
        #
        #   0 + (2 ** 2) - 1 = 3
        #   ^      ^       ^
        #   |      |       offset for zero-indexing
        #   |      |
        #   |      table level
        #   |
        #   start of query
        #
        # For range_2_index, it's simpler because we just need to query the
        # index corresponding to the end point of our range query, since we
        # know (by definition) that the value at index "end" corresponds to
        # the window whose right-most endpoint exactly lines up with our
        # query endpoint. Thus, in this example, we query index 5 on the
        # table level corresponding to the windows of size 2**2.
        range_1_index = self.initial_query.start + window_size - 1
        range_2_index = self.initial_query.end - 1

        # This is a minor optimization to first define a set {...} to
        # remove duplicates, then convert to a list to match the return
        # type of the `RangeAggregateQuerier` interface.
        return list({(power, range_1_index), (power, range_2_index)})

    def resolve(self, responses: List[int]) -> ResolveDone:
        if len(responses) <= 0:
            raise ValueError("responses cannot be empty")
        return ResolveDone(min(responses))
