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
import math

from typing import List, Tuple, Union, Dict

from hypothesis import given
from hypothesis.strategies import integers, lists
from parameterized import parameterized

from arca.arq.plaintext_schemes.median import MedianAlphaApprox
from arca.arq.plaintext_schemes.median.median_alpha_approx import (
    MedianAlphaApproxQuerier,
)
from arca.arq.range_aggregate_querier import ResolveDone
from arca.arq import ARQ, Domain, Table, Table, RangeQuery
from arca.ste.edx import SimpleEDX
from arca.ste.serializers import IntSerializer, StructSerializer, PickleSerializer

from decimal import Decimal
from fractions import Fraction

DEFAULT_ALPHA = Fraction("1/2")


def is_alpha_approximate_median(
    alpha: Union[float, Decimal, Fraction],
    median_candidate: int,
    table: Table,
    range_query: RangeQuery,
) -> bool:
    """
    Returns true if the given :paramref:`median_candidate` is a
    :paramref:`alpha`-approximate mode for the given :paramref:`range_query`
    on the given :paramref:`table`.

    :param alpha: the alpha
    :param median_candidate: the approximate median to validate
    :param table: the table
    :param range_query: the range query that the approximate median came from
    :return: :py:const:`True` if :paramref:`median_candidate` is a
        :paramref:`alpha`-approximate mode; otherwise, :py:const:`False`
    """
    entries = table.filter_range(range_query)
    if range_query.length() == 1:
        return median_candidate in entries

    median_rank = math.ceil(range_query.length() / 2) - 1
    lower_bound = math.ceil(alpha * median_rank) - 1
    upper_bound = range_query.length() - lower_bound + 1

    for index, sorted_entry in enumerate(sorted(entries)):
        if median_candidate == sorted_entry:
            rank = index + 1
            if lower_bound <= rank <= upper_bound:
                return True
    return False


class TestMedianAlphaApprox(unittest.TestCase):
    def setUp(self):
        self.eds_scheme = SimpleEDX(
            dx_key_serializer=StructSerializer(format_string="ii"),
            dx_value_serializer=PickleSerializer(),
        )
        self.aggregate_scheme = MedianAlphaApprox(alpha=DEFAULT_ALPHA)
        self.arq_scheme = ARQ(
            eds_scheme=self.eds_scheme, aggregate_scheme=self.aggregate_scheme
        )

    @parameterized.expand(
        [
            (
                True,
                0.5,
                0,
                Table.make_from_list(
                    [
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                    ]
                ),
                RangeQuery(start=1, end=20),
            ),
            (
                True,
                0.5,
                1,
                Table.make_from_list(
                    [
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        1,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                    ]
                ),
                RangeQuery(start=1, end=20),
            ),
            (True, 0.5, 0, Table.make_from_list([0]), RangeQuery(start=0, end=1)),
            (True, 0.5, 0, Table.make_from_list([0, 0, 0]), RangeQuery(start=0, end=1)),
            (True, 0.5, 0, Table.make_from_list([0, 0, 0]), RangeQuery(start=0, end=1)),
            (
                True,
                0.5,
                0,
                Table.make_from_list([0, 0, 0, 0, 0, 0, 0, 0]),
                RangeQuery(start=0, end=7),
            ),
            (
                True,
                0.5,
                0,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (
                True,
                0.5,
                1,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (
                True,
                0.5,
                2,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (
                True,
                0.5,
                3,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (
                True,
                0.5,
                4,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (
                True,
                0.5,
                5,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (
                True,
                0.5,
                6,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (
                False,
                0.5,
                7,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (
                False,
                0.75,
                0,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (
                True,
                0.75,
                1,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (
                True,
                0.75,
                2,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (
                True,
                0.75,
                3,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (
                True,
                0.75,
                4,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (
                True,
                0.75,
                5,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (
                False,
                0.75,
                6,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (
                False,
                0.75,
                7,
                Table.make_from_list([0, 1, 2, 3, 4, 5, 6, 7]),
                RangeQuery(start=0, end=7),
            ),
            (True, 0.5, 0, Table.make_from_list([1, 0, 0]), RangeQuery(start=0, end=2)),
            (True, 0.5, 1, Table.make_from_list([1, 0, 0]), RangeQuery(start=0, end=2)),
        ]
    )
    def test_is_alpha_approximate_median(
        self, expected_result, alpha, median_candidate, table, range_query
    ) -> None:
        self.assertEqual(
            is_alpha_approximate_median(alpha, median_candidate, table, range_query),
            expected_result,
        )

    @parameterized.expand(
        [
            (
                [0, 1, 1, 1, 0],
                Fraction("1/8"),
                {
                    (1, 1): [1, 1, 1],
                    (1, 2): [0, 0, 0],
                    (2, 1): [0, 1, 1],
                    (2, 2): [1, 1, 1],
                    (2, 3): [0, 0, 0],
                    (3, 1): [0, 0, 1],
                    (3, 2): [1, 1, 1],
                    (3, 3): [1, 1, 1],
                    (3, 4): [1, 0, 0],
                    (3, 5): [0, 0, 0],
                },
            ),
            (
                [0, 1, 1, 1, 2, 3, 3, 4, 3, 1, 2, 4, 4, 1, 4, 0],
                Fraction("1/8"),
                {
                    (1, 1): [1, 2, 2],
                    (1, 2): [2, 2, 2],
                    (2, 1): [1, 1, 2],
                    (2, 2): [3, 3, 3],
                    (2, 3): [2, 2, 2],
                    (2, 4): [1, 1, 1],
                    (3, 1): [0, 1, 1],
                    (3, 2): [1, 1, 2],
                    (3, 3): [2, 3, 3],
                    (3, 4): [3, 3, 3],
                    (3, 5): [1, 2, 2],
                    (3, 6): [2, 2, 2],
                    (3, 7): [1, 1, 1],
                    (3, 8): [0, 0, 0],
                    (4, 1): [0, 0, 1],
                    (4, 2): [1, 1, 1],
                    (4, 3): [1, 1, 1],
                    (4, 4): [1, 1, 2],
                    (4, 5): [2, 2, 3],
                    (4, 6): [3, 3, 3],
                    (4, 7): [3, 3, 3],
                    (4, 8): [4, 3, 3],
                    (4, 9): [3, 1, 2],
                    (4, 10): [1, 1, 2],
                    (4, 11): [2, 2, 4],
                    (4, 12): [4, 4, 4],
                    (4, 13): [4, 1, 4],
                    (4, 14): [1, 1, 1],
                    (4, 15): [4, 0, 0],
                    (4, 16): [0, 0, 0],
                },
            ),
            (
                [0, 1, 2, 3, 4, 5],
                Fraction("1/8"),
                {
                    (1, 1): [1, 2, 2],
                    (1, 2): [4, 4, 4],
                    (2, 1): [0, 1, 2],
                    (2, 2): [2, 3, 3],
                    (2, 3): [4, 4, 4],
                    (3, 1): [0, 0, 1],
                    (3, 2): [1, 1, 2],
                    (3, 3): [2, 2, 3],
                    (3, 4): [3, 3, 4],
                    (3, 5): [4, 4, 4],
                    (3, 6): [5, 5, 5],
                },
            ),
            (
                [0, 0, 0, 0, 0, 0, 0, 0],
                Fraction("1/8"),
                {
                    (1, 1): [0, 0, 0],
                    (1, 2): [0, 0, 0],
                    (2, 1): [0, 0, 0],
                    (2, 2): [0, 0, 0],
                    (2, 3): [0, 0, 0],
                    (2, 4): [0, 0, 0],
                    (3, 1): [0, 0, 0],
                    (3, 2): [0, 0, 0],
                    (3, 3): [0, 0, 0],
                    (3, 4): [0, 0, 0],
                    (3, 5): [0, 0, 0],
                    (3, 6): [0, 0, 0],
                    (3, 7): [0, 0, 0],
                    (3, 8): [0, 0, 0],
                },
            ),
        ]
    )
    def test_median_alpha_approx_setup(
        self,
        lst: List[int],
        alpha: Fraction,
        expected_ds: Dict[Tuple[int, int, int], int],
    ) -> None:
        """
        MedianAlphaApprox-specific unit test for checking that the
        MedianAlphaApprox setup algorithm generates the correct data structure.
        """
        self.maxDiff = None
        table = Table.make_from_list(lst)
        aggregate_scheme = MedianAlphaApprox(alpha=alpha)
        self.assertEqual(
            aggregate_scheme.setup(table),
            expected_ds,
        )

    @parameterized.expand(
        [
            (
                Domain(start=0, end=5),
                Fraction("1/2"),
                RangeQuery(start=3, end=4),
                (3, 4, 0),
            ),
            (
                Domain(start=0, end=6),
                Fraction("1/2"),
                RangeQuery(start=3, end=5),
                (3, 4, 1),
            ),
            (
                Domain(start=0, end=4),
                Fraction("1/2"),
                RangeQuery(start=0, end=1),
                (2, 1, 0),
            ),
            (
                Domain(start=0, end=16),
                Fraction("1/2"),
                RangeQuery(start=0, end=4),
                (3, 1, 1),
            ),
            (
                Domain(start=0, end=8),
                Fraction("1/2"),
                RangeQuery(start=1, end=7),
                (2, 2, 1),
            ),
            (
                Domain(start=0, end=16),
                Fraction("1/2"),
                RangeQuery(start=0, end=3),
                (4, 1, 2),
            ),
            (
                Domain(start=0, end=16),
                Fraction("1/2"),
                RangeQuery(start=0, end=11),
                (2, 1, 1),
            ),
            (
                Domain(start=0, end=16),
                Fraction("1/2"),
                RangeQuery(start=1, end=11),
                (2, 2, 0),
            ),
            (
                Domain(start=0, end=16),
                Fraction("1/2"),
                RangeQuery(start=1, end=12),
                (2, 2, 1),
            ),
            (
                Domain(start=0, end=16),
                Fraction("1/2"),
                RangeQuery(start=1, end=6),
                (3, 2, 1),
            ),
            (
                Domain(start=0, end=16),
                Fraction("1/2"),
                RangeQuery(start=1, end=7),
                (3, 2, 1),
            ),
            (
                Domain(start=0, end=16),
                Fraction("1/2"),
                RangeQuery(start=1, end=9),
                (2, 2, 0),
            ),
        ]
    )
    def test_median_alpha_approx_querier(
        self,
        domain: Domain,
        alpha: Fraction,
        range_query: RangeQuery,
        expected_query: Tuple[int, int, int],
    ) -> None:
        """
        MedianAlphaApprox-specific unit test for checking that the
        MedianAlphaApproxQuerier generates the correct queries.
        """
        aggregate_scheme = MedianAlphaApprox(alpha=alpha)
        querier = aggregate_scheme.generate_querier(domain=domain, query=range_query)
        queries = querier.query()
        self.assertEqual(len(queries), 1)
        self.assertEqual(queries[0], (expected_query[0], expected_query[1]))
        self.assertEqual(querier.p, expected_query[2])

    @given(lists(integers(min_value=-1 * (2**16), max_value=2**16), min_size=1))
    def test_median_alpha_approx(self, entries: List[int]) -> None:
        """
        Test for plaintext MedianAlphaApprox scheme correctness.
        """
        table = Table.make_from_list(entries)

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
                self.assertTrue(
                    is_alpha_approximate_median(
                        DEFAULT_ALPHA, resolve_output.aggregate, table, range_query
                    ),
                )

    @given(lists(integers(min_value=-1 * (2**16), max_value=2**16), min_size=1))
    def test_mode_as_table_with_arq(self, entries: List[Tuple[str, str]]) -> None:
        """
        Test for correctness of the ARQ instantiation with the ModeASTable
        scheme.
        """
        table = Table.make(list(enumerate(entries)))
        key = self.arq_scheme.generate_key()
        eds_serialized = self.arq_scheme.setup(key, table)
        eds = self.arq_scheme.load_eds(eds_serialized)

        for query_start in range(table.domain.start, table.domain.end - 1):
            for query_end in range(query_start + 1, table.domain.end):
                range_query = RangeQuery(start=query_start, end=query_end)
                actual_result = self.arq_scheme.query(
                    key, table.domain, range_query, eds
                )

                self.assertTrue(
                    is_alpha_approximate_median(
                        DEFAULT_ALPHA, actual_result, table, range_query
                    ),
                )
