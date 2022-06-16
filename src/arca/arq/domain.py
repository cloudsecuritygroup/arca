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

from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Domain:
    """
    Represents the range of queryable values in a :class:`Table`.
    """

    __slots__ = ["start", "end"]

    #: Start of the domain (inclusive).
    start: int
    #: End of the domain (exclusive).
    end: int

    @lru_cache
    def size(self) -> int:
        """
        Returns the number of possible domain values. In other words,
        size = end - start.

        :return: the size of the :class:`Domain`
        """
        return self.end - self.start
