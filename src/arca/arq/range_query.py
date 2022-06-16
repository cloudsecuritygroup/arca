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

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterator, Tuple

from .domain import Domain


import math
import random


@dataclass(frozen=True)
class RangeQuery:
    """
    Represents a range query.
    """

    __slots__ = ["start", "end"]
    #: Start of the range (inclusive).
    start: int
    #: End of the range (exclusive).https://github.com/cloudsecuritygroup/arca/blob/main/CITATION.cff
    end: int

    @lru_cache
    def length(self) -> int:
        """
        Returns the number of domain values contained within the query. In
        other words, length = end - start.

        :return: the length of the :class:`RangeQuery`
        """
        return self.end - self.start

    @staticmethod
    def enumerate_all(domain: Domain) -> Iterator[RangeQuery]:
        for query_start in range(domain.start, domain.end):
            for query_end in range(query_start + 1, domain.end + 1):
                yield RangeQuery(start=query_start, end=query_end)

    @staticmethod
    def enumerate_samples_from_buckets(
        domain: Domain, *, bucket_size: int, num_samples_per_bucket: int
    ) -> Iterator[Tuple[int, RangeQuery]]:

        number_of_buckets = math.ceil(100 / bucket_size)

        percentile_bounds = {}

        for bucket in range(number_of_buckets):
            percentile = (bucket + 1) * bucket_size
            bucket_length = math.floor((percentile / 100) * domain.size())

            start_upper_bound = max(domain.end - bucket_length - 1, domain.start)
            percentile_bounds[percentile] = start_upper_bound

        for percentile, start_ub in percentile_bounds.items():
            bucket_length = math.floor((percentile / 100) * domain.size())
            if bucket_length >= 1:
                for _ in range(num_samples_per_bucket):
                    start = random.randint(domain.start, start_ub)
                    end = min(start + bucket_length, domain.end)
                    yield (percentile, RangeQuery(start=start, end=end))

        # # number_of_buckets = math.ceil(100 / bucket_size)
        # # buckets = defaultdict(list)
        # # for range_query in RangeQuery.enumerate_all(domain):
        # #     bucket = (
        # #         math.floor(range_query.length() / domain.size() * number_of_buckets)
        # #         * bucket_size
        # #     )
        # #     buckets[bucket].append(range_query)

        # for bucket, queries_in_bucket in buckets.items():
        #     seen_samples = 0
        #     while seen_samples < num_samples_per_bucket:
        #         seen_samples += 1
        #         query_to_yield = random.sample(queries_in_bucket, k=1)[0]
        #         yield (bucket, query_to_yield)
