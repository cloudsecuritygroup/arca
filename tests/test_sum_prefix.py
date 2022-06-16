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

import unittest

from typing import List, Tuple

from hypothesis import given, settings
from hypothesis.strategies import tuples, integers, lists

from arca.arq.plaintext_schemes.sum import SumPrefix
from arca.arq.range_aggregate_querier import ResolveDone
from arca.arq.arq import ARQ
from arca.arq.table import Table
from arca.arq.range_query import RangeQuery
from arca.ste.edx import SimpleEDX
from arca.ste.serializers import IntSerializer


class TestSumPrefix(unittest.TestCase):
    def setUp(self):
        self.eds_scheme = SimpleEDX(
            dx_key_serializer=IntSerializer(), dx_value_serializer=IntSerializer()
        )
        self.aggregate_scheme = SumPrefix()
        self.arq_scheme = ARQ(
            eds_scheme=self.eds_scheme, aggregate_scheme=self.aggregate_scheme
        )

    @given(lists(tuples(integers(min_value=0, max_value=100), integers()), min_size=1))
    def test_sum_prefix(self, entries: List[Tuple[str, str]]) -> None:
        """
        Test for plaintext SumPrefix scheme correctness.
        """
        table = Table.make(entries)

        plaintext_ds = self.aggregate_scheme.setup(table)

        for query_start in range(table.domain.start, table.domain.end - 1):
            for query_end in range(query_start + 1, table.domain.end):
                range_query = RangeQuery(start=query_start, end=query_end)
                querier = self.aggregate_scheme.generate_querier(
                    table.domain, range_query
                )

                responses = [plaintext_ds[query] for query in querier.query()]
                resolve_output = querier.resolve(responses)
                self.assertTrue(isinstance(resolve_output, ResolveDone))
                expected_result = sum(table.filter_range(range_query))
                self.assertEqual(expected_result, resolve_output.aggregate)

    @settings(deadline=None)
    @given(
        lists(
            tuples(
                # These bounds are small just to make the ARQ enumeration in
                # SimpleEDX not too long.
                integers(min_value=-16, max_value=16),
                # These bounds are almost the bit size bounds of struct's "i"
                # format; anything larger will probably eventually overflow the
                # bounds as the running sum is counted in the prefix sum scheme.
                integers(min_value=-1 * (2**28), max_value=2**28),
            ),
            min_size=1,
        )
    )
    def test_sum_prefix_with_arq(self, entries: List[Tuple[str, str]]) -> None:
        """
        Test for correctness of the ARQ instantiation with the SumPrefix scheme.
        """
        table = Table.make(entries)
        key = self.arq_scheme.generate_key()
        eds_serialized = self.arq_scheme.setup(key, table)
        eds = self.arq_scheme.load_eds(eds_serialized)

        for query_start in range(table.domain.start, table.domain.end - 1):
            for query_end in range(query_start + 1, table.domain.end):
                range_query = RangeQuery(start=query_start, end=query_end)
                actual_result = self.arq_scheme.query(
                    key, table.domain, range_query, eds
                )

                expected_result = sum(table.filter_range(range_query))
                self.assertEqual(expected_result, actual_result)
