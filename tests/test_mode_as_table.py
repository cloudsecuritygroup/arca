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

from typing import List, Tuple, Dict
from statistics import mode
from collections import Counter

from hypothesis import given
from hypothesis.strategies import integers, lists
from parameterized import parameterized

from arca.arq.plaintext_schemes.mode import ModeASTable
from arca.arq.range_aggregate_querier import ResolveDone
from arca.arq import ARQ, Domain, Table, Table, RangeQuery
from arca.ste.edx import SimpleEDX
from arca.ste.serializers import StructSerializer

ALPHA = 0.5


def is_alpha_approximate_mode(
    alpha: float, mode_candidate: int, table: Table, range_query: RangeQuery
) -> bool:
    """
    Returns true if the given :paramref:`mode_candidate` is a
    :paramref:`alpha`-approximate mode for the given :paramref:`range_query`
    on the given :paramref:`table`.

    :param alpha: the alpha
    :param mode_candidate: the approximate mode to validate
    :param table: the table
    :param range_query: the range query that the approximate mode came from
    :return: :py:const:`True` if :paramref:`mode_candidate` is a
        :paramref:`alpha`-approximate mode; otherwise, :py:const:`False`
    """
    entries = table.filter_range(range_query)
    frequencies = Counter(entries)
    actual_mode = mode(entries)
    freq_candidate = frequencies[mode_candidate]
    freq_actual = frequencies[actual_mode]
    return freq_candidate >= (alpha * freq_actual)


class TestMinimumSparseTable(unittest.TestCase):
    def setUp(self):
        self.eds_scheme = SimpleEDX(
            dx_key_serializer=StructSerializer(format_string="ii"),
            dx_value_serializer=StructSerializer(format_string="ii"),
        )
        self.aggregate_scheme = ModeASTable()
        self.arq_scheme = ARQ(
            eds_scheme=self.eds_scheme, aggregate_scheme=self.aggregate_scheme
        )

    @given(lists(integers(min_value=-10, max_value=10), min_size=1))
    def test_mode_as_table(self, entries: List[int]) -> None:
        """
        Test for plaintext ModeASTable scheme correctness.
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
                    is_alpha_approximate_mode(
                        ALPHA, resolve_output.aggregate, table, range_query
                    )
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
                    is_alpha_approximate_mode(ALPHA, actual_result, table, range_query)
                )

    def test_is_alpha_approximate_mode(self) -> None:
        self.assertTrue(
            is_alpha_approximate_mode(
                ALPHA, 0, Table.make_from_list([0, 0, 0, 0]), RangeQuery(start=0, end=4)
            )
        )
        self.assertTrue(
            is_alpha_approximate_mode(
                ALPHA, 0, Table.make_from_list([0, 1, 1]), RangeQuery(start=0, end=3)
            ),
        )
        self.assertTrue(
            is_alpha_approximate_mode(
                ALPHA, 0, Table.make_from_list([0, 0, 1, 1]), RangeQuery(start=0, end=4)
            )
        )
        self.assertTrue(
            is_alpha_approximate_mode(
                ALPHA,
                0,
                Table.make_from_list([0, 0, 1, 1, 1]),
                RangeQuery(start=0, end=5),
            )
        )
        self.assertFalse(
            is_alpha_approximate_mode(
                ALPHA, 0, Table.make_from_list([0, 1, 1, 1]), RangeQuery(start=0, end=4)
            )
        )

    @parameterized.expand(
        [
            (RangeQuery(start=0, end=1), [(0, 0)]),
            (RangeQuery(start=0, end=2), [(1, 0), (1, 1)]),
            (RangeQuery(start=0, end=3), [(2, 0), (2, 2)]),
            (RangeQuery(start=0, end=4), [(2, 0), (2, 3)]),
            (RangeQuery(start=0, end=5), [(3, 0), (3, 4)]),
            (RangeQuery(start=1, end=5), [(3, 1), (3, 4)]),
            (RangeQuery(start=2, end=5), [(3, 2), (3, 4)]),
            (RangeQuery(start=3, end=5), [(3, 3), (3, 4)]),
            (RangeQuery(start=4, end=5), [(0, 4)]),
            (RangeQuery(start=2, end=8), [(3, 2), (3, 7)]),
            (RangeQuery(start=2, end=9), [(4, 2), (4, 8)]),
            (RangeQuery(start=2, end=12), [(4, 2), (4, 11)]),
            (RangeQuery(start=11, end=14), [(3, 11), (3, 13)]),
        ]
    )
    def test_mode_as_table_querier(
        self, range_query: RangeQuery, expected_queries: List[Tuple[int, int]]
    ) -> None:
        """
        ModeASTable-specific unit test for checking that the ModeASTableQuerier
        generates the correct queries.
        """
        DOMAIN = Domain(start=0, end=1)  # the domain shouldn't matter
        querier = self.aggregate_scheme.generate_querier(
            domain=DOMAIN, query=range_query
        )
        self.assertCountEqual(querier.query(), expected_queries)

    @parameterized.expand(
        [
            (
                [0, 0, 0, 0],
                {
                    (0, 0): (0, 1),
                    (0, 1): (0, 1),
                    (0, 2): (0, 1),
                    (0, 3): (0, 1),
                    (1, 0): (0, 1),
                    (1, 1): (0, 1),
                    (1, 2): (0, 1),
                    (1, 3): (0, 1),
                    (2, 0): (0, 2),
                    (2, 1): (0, 1),
                    (2, 2): (0, 1),
                    (2, 3): (0, 2),
                },
            ),
            (
                [1, 1, 0, 0],
                {
                    (0, 0): (1, 1),
                    (0, 1): (1, 1),
                    (0, 2): (0, 1),
                    (0, 3): (0, 1),
                    (1, 0): (1, 1),
                    (1, 1): (1, 1),
                    (1, 2): (0, 1),
                    (1, 3): (0, 1),
                    (2, 0): (1, 2),
                    (2, 1): (1, 1),
                    (2, 2): (0, 1),
                    (2, 3): (0, 2),
                },
            ),
            (
                [0, 0, 1, 1, 2, 2, 3, 3],
                {
                    (0, 0): (0, 1),
                    (0, 1): (0, 1),
                    (0, 2): (1, 1),
                    (0, 3): (1, 1),
                    (0, 4): (2, 1),
                    (0, 5): (2, 1),
                    (0, 6): (3, 1),
                    (0, 7): (3, 1),
                    (1, 0): (0, 1),
                    (1, 1): (0, 1),
                    (1, 2): (1, 1),
                    (1, 3): (1, 1),
                    (1, 4): (2, 1),
                    (1, 5): (2, 1),
                    (1, 6): (3, 1),
                    (1, 7): (3, 1),
                    (2, 0): (0, 2),
                    (2, 1): (0, 1),
                    (2, 2): (1, 1),
                    (2, 3): (1, 2),
                    (2, 4): (2, 2),
                    (2, 5): (2, 1),
                    (2, 6): (3, 1),
                    (2, 7): (3, 2),
                    (3, 0): (1, 2),
                    (3, 1): (1, 2),
                    (3, 2): (1, 2),
                    (3, 3): (1, 1),
                    (3, 4): (2, 1),
                    (3, 5): (2, 2),
                    (3, 6): (2, 2),
                    (3, 7): (2, 2),
                },
            ),
            (
                [0, 0, 1, 1, 2, 2, 3],
                {
                    (0, 0): (0, 1),
                    (0, 1): (0, 1),
                    (0, 2): (1, 1),
                    (0, 3): (1, 1),
                    (0, 4): (2, 1),
                    (0, 5): (2, 1),
                    (0, 6): (3, 1),
                    (1, 0): (0, 1),
                    (1, 1): (0, 1),
                    (1, 2): (1, 1),
                    (1, 3): (1, 1),
                    (1, 4): (2, 1),
                    (1, 5): (2, 1),
                    (1, 6): (3, 1),
                    (2, 0): (0, 2),
                    (2, 1): (0, 1),
                    (2, 2): (1, 1),
                    (2, 3): (1, 2),
                    (2, 4): (2, 2),
                    (2, 5): (2, 1),
                    (2, 6): (3, 1),
                    (3, 0): (1, 2),
                    (3, 1): (1, 2),
                    (3, 2): (1, 2),
                    (3, 3): (1, 1),
                    (3, 4): (2, 1),
                    (3, 5): (2, 2),
                    (3, 6): (2, 2),
                },
            ),
            (
                [0, 0, 1, 1, 2, 2],
                {
                    (0, 0): (0, 1),
                    (0, 1): (0, 1),
                    (0, 2): (1, 1),
                    (0, 3): (1, 1),
                    (0, 4): (2, 1),
                    (0, 5): (2, 1),
                    (1, 0): (0, 1),
                    (1, 1): (0, 1),
                    (1, 2): (1, 1),
                    (1, 3): (1, 1),
                    (1, 4): (2, 1),
                    (1, 5): (2, 1),
                    (2, 0): (0, 2),
                    (2, 1): (0, 1),
                    (2, 2): (1, 1),
                    (2, 3): (1, 2),
                    (2, 4): (2, 2),
                    (2, 5): (2, 1),
                    (3, 0): (1, 2),
                    (3, 1): (1, 2),
                    (3, 2): (1, 2),
                    (3, 3): (1, 1),
                    (3, 4): (2, 1),
                    (3, 5): (2, 2),
                },
            ),
        ]
    )
    def test_mode_as_table_setup(
        self, lst: List[int], expected_ds: Dict[Tuple[int, int], Tuple[int, int]]
    ) -> None:
        """
        ModeASTable-specific unit test for checking that the ModeASTable setup
        algorithm generates the correct data structure.
        """
        table = Table.make_from_list(lst)
        self.assertEqual(
            self.aggregate_scheme.setup(table),
            expected_ds,
        )
