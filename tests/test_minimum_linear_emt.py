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

from hypothesis import given
from hypothesis.strategies import integers, lists
from parameterized import parameterized

from arca.arq.plaintext_schemes.minimum import MinimumLinearEMT
from arca.arq.range_aggregate_querier import ResolveDone
from arca.arq.arq import ARQ
from arca.arq.table import Table
from arca.arq.range_query import RangeQuery
from arca.ste.edx import SimpleEDX
from arca.ste.serializers import PickleSerializer, IntSerializer


class TestMinimumLinearEMT(unittest.TestCase):
    def setUp(self):
        self.eds_scheme = SimpleEDX(
            dx_key_serializer=PickleSerializer(), dx_value_serializer=IntSerializer()
        )
        self.aggregate_scheme = MinimumLinearEMT()
        self.arq_scheme = ARQ(
            eds_scheme=self.eds_scheme, aggregate_scheme=self.aggregate_scheme
        )

    @parameterized.expand(
        [
            (1, 1),
            (2, 1),
            (3, 2),
            (4, 2),
            (7, 3),
            (9, 4),
            (16, 4),
            (17, 5),
        ]
    )
    def test_linear_minimum_emt_compute_block_size_fixed(
        self, domain_size: int, expected_block_size: int
    ) -> None:
        self.assertEqual(
            MinimumLinearEMT.compute_block_size(domain_size), expected_block_size
        )

    @given(integers(min_value=1, max_value=64))
    def test_linear_minimum_emt_compute_block_size_hypothesis(self, power: int) -> None:
        self.assertEqual(MinimumLinearEMT.compute_block_size(2**power), power)

    @given(lists(integers(min_value=-1 * (2**31), max_value=2**31), min_size=1))
    def test_linear_minimum_emt(self, entries: List[Tuple[str, str]]) -> None:
        """
        Test for plaintext MinimumLinearEMT scheme correctness.
        """
        table = Table.make(list(enumerate(entries)))
        block_size = MinimumLinearEMT.compute_block_size(table.domain.size())

        plaintext_ds = self.aggregate_scheme.setup(table)

        for range_query in RangeQuery.enumerate_all(table.domain):
            # We only allow queries that are larger than or equal to the
            # block size:
            if range_query.end - range_query.start >= block_size:
                querier = self.aggregate_scheme.generate_querier(
                    table.domain, range_query
                )

                responses = [plaintext_ds[query] for query in querier.query()]
                resolve_output = querier.resolve(responses)
                self.assertTrue(isinstance(resolve_output, ResolveDone))
                expected_result = min(table.filter_range(range_query))
                self.assertEqual(expected_result, resolve_output.aggregate)

    @given(lists(integers(min_value=-1 * (2**31), max_value=2**31), min_size=1))
    def test_linear_minimum_emt_with_arq(self, entries: List[Tuple[str, str]]) -> None:
        """
        Test for correctness of the ARQ instantiation with the LinearMinimumEMT
        scheme.
        """
        table = Table.make(list(enumerate(entries)))
        block_size = MinimumLinearEMT.compute_block_size(table.domain.size())

        key = self.arq_scheme.generate_key()
        eds_serialized = self.arq_scheme.setup(key, table)
        eds = self.arq_scheme.load_eds(eds_serialized)

        for range_query in RangeQuery.enumerate_all(table.domain):
            # We only allow queries that are larger than or equal to the
            # block size:
            if range_query.end - range_query.start >= block_size:
                actual_result = self.arq_scheme.query(
                    key, table.domain, range_query, eds
                )

                expected_result = min(table.filter_range(range_query))
                self.assertEqual(expected_result, actual_result)
