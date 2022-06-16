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
from collections import defaultdict
from tqdm import trange

import math
import statistics


class ModeASTable(
    RangeAggregateScheme[
        Dict[Tuple[int, int], Tuple[int, int]], Tuple[int, int], Tuple[int, int]
    ]
):
    """
    Implements the one-dimensional sparse table technique for approximate
    range mode queries from [BKMT05].

    The table's windows look something like this:

    .. code-block: text

        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
                    |___|___|
                  |_____|_____|
                |_______|_______|
              |_________|_________|
            |___________|___________|
          |_____________|_____________|
        |_______________|_______________|
            |___|___|
          |_____|_____|
        |_______|_______|
                            |___|___|
                          |_____|_____|
                        |_______|_______|

                  ... and so on

    (This is a really rough sketch that doesn't really capture everything,
    so you probably should read the paper for more details.)
    """

    def setup(self, table: Table) -> Dict[Tuple[int, int], Tuple[int, int]]:
        as_table_ds: Dict[Tuple[int, int], Tuple[int, int]] = {}

        ending_power_of_2 = log2_ceil(table.domain.size())
        table_points = list(
            table.iterate_over_unique_domain_points(
                lambda lst: statistics.mode(lst)
                if len(lst) > 0
                else 0  # TODO(zespirit): this needs to output counts, not the mode
            )
        )
        for power in trange(ending_power_of_2 + 1, leave=False):
            range_size = 2**power
            num_segments = math.ceil(table.domain.size() / range_size)

            for segment_index in trange(num_segments, leave=False):
                start = segment_index * range_size
                end = min(start + range_size, table.domain.size())
                halfway = min(start + int(range_size / 2), end)

                ds1 = self.__running_mode(
                    table_points, power, reversed(range(start, halfway))
                )
                ds2 = self.__running_mode(table_points, power, range(halfway, end))
                as_table_ds = {**as_table_ds, **ds1, **ds2}

        return as_table_ds

    def generate_querier(self, domain: Domain, query: RangeQuery) -> ModeASTableQuerier:
        return ModeASTableQuerier(domain=domain, initial_query=query)

    def __running_mode(
        self, table_points: List[int], level: int, iterator: Iterable[int]
    ) -> Dict[Tuple[int, int], Tuple[int, int]]:
        as_table_ds = {}

        counts: Dict[int, int] = defaultdict(lambda: 0)
        current_mode = 0
        current_count = 0
        for i in iterator:
            value = table_points[i]
            counts[value] += 1
            if counts[value] > current_count:
                current_mode = value
                current_count = counts[value]
            as_table_ds[(level, i)] = (current_mode, current_count)

        return as_table_ds


@dataclass(frozen=True)
class ModeASTableQuerier(RangeAggregateQuerier[Tuple[int, int], Tuple[int, int]]):
    """
    Associated querier for the :class:`ModeASTable` scheme.
    """

    domain: Domain
    initial_query: RangeQuery

    def query(self) -> List[Tuple[int, int]]:
        start = self.initial_query.start
        end = self.initial_query.end - 1
        level = (start ^ end).bit_length()
        return list({(level, start), (level, end)})

    def resolve(self, responses: List[Tuple[int, int]]) -> ResolveDone:
        if len(responses) <= 0:
            raise ValueError("responses cannot be empty")
        maximal_mode_tuple = max(responses, key=lambda tup: tup[1])
        return ResolveDone(maximal_mode_tuple[0])
