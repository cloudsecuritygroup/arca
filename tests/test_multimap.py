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
from hypothesis.strategies import tuples, text, lists

from arca.ste.emm.multimap import Multimap


class TestMultimap(unittest.TestCase):
    def test_multimap_fixed(self) -> None:
        mm: Multimap[str, int] = Multimap()

        mm.set("a", 1)
        mm.set("a", 2)
        mm.set("a", 3)

        mm.set("b", 4)

        mm.set("c", 5)
        mm.set("c", 6)

        self.assertCountEqual(mm.get("a"), [1, 2, 3])
        self.assertCountEqual(mm.get("b"), [4])
        self.assertCountEqual(mm.get("c"), [5, 6])

        mm.delete("b")

        self.assertCountEqual(mm.get("a"), [1, 2, 3])
        self.assertEqual(mm.get("b"), None)
        self.assertCountEqual(mm.get("c"), [5, 6])

    @given(lists(tuples(text(), text())))
    def test_multimap_generated(self, entries: List[Tuple[str, str]]) -> None:
        mm: Multimap[str, str] = Multimap()

        for key, value in entries:
            mm.set(key, value)

        original_keys = set(map(lambda x: x[0], entries))
        mm_keys = set()
        for key, entries in mm:
            mm_keys.add(key)

        self.assertEqual(original_keys, mm_keys)
