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

from typing import Callable, Dict, Iterable, Iterator, List, Tuple
from dataclasses import dataclass
from collections import defaultdict

from .range_query import RangeQuery
from .domain import Domain

# import numpy as np
# import pandas as pd


@dataclass(frozen=True)
class Table:
    """
    Represents a collection of records.
    """

    __slots__ = ["entries", "domain"]
    entries: Dict[int, List[int]]
    domain: Domain

    def number_of_filled_domain_points(self) -> int:
        return len(self.entries.keys())

    def number_of_records(self) -> int:
        return sum(map(lambda lst: len(lst), self.entries.values()))

    def filter(self, domain_value: int) -> List[int]:
        """
        Returns all of the records with matching domain_value. The
        returned List is not in any defined order (only used to
        allow for duplicates).

        :param domain_value: the domain value to filter for
        :return: a List of all records located at the particular domain_value
        """
        return self.entries.get(domain_value, list())

    def filter_range(self, range_query: RangeQuery) -> List[int]:
        """
        Returns all of the records contained in the given range_query.
        The returned List is not in any defined order (only used to
        allow for duplicates).

        :param range_query: the range to filter over
        :return: a List of all records matching the filter
        """
        result: List[int] = []
        for domain_value in range(range_query.start, range_query.end):
            result = result + self.filter(domain_value)
        return result

    def iterate_over_unique_domain_points(
        self, disambiguator: Callable[[List[int]], int]
    ) -> Iterator[int]:
        for domain_value in range(self.domain.start, self.domain.end):
            yield disambiguator(self.filter(domain_value))

    @staticmethod
    def make(records: Iterable[Tuple[int, int]]) -> Table:
        """
        Makes a table from the records in the given iterator.

        :param records: the records to generate the :class:`Table` from
        :return: a new :class:`Table`
        """
        # df = pd.DataFrame(records)
        # df = df.set_index(df.columns[0])
        # df = df.reindex(list(range(0, df.index.max() + 1)), fill_value=0)

        # domain = Domain(start=df.index.min(), end=df.index.max())

        domain_start = min(records, key=lambda tup: tup[0])[0]
        domain_end = (
            max(records, key=lambda tup: tup[0])[0] + 1
        )  # + 1 since Domain is exclusive of the end point
        domain = Domain(start=domain_start, end=domain_end)

        mapping: Dict[int, List[int]] = defaultdict(list)
        for attr1, attr2 in records:
            mapping[attr1].append(attr2)
        return Table(entries=mapping, domain=domain)

    @staticmethod
    def make_from_list(records: List[int]) -> Table:
        return Table.make(list(enumerate(records)))
