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

from typing import Dict, Generic, Iterator, List, Optional, Tuple, TypeVar
from collections import defaultdict
from dataclasses import dataclass, field

KeyType = TypeVar("KeyType")
ValueType = TypeVar("ValueType")


@dataclass
class Multimap(Generic[KeyType, ValueType]):
    """
    A multimap.

    The internal representation of :class:`Multimap` uses lists, so duplicate
    entries for the same key are permitted.
    """

    multimap: Dict[KeyType, List[ValueType]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def set(self, key: KeyType, element: ValueType) -> None:
        """
        Adds the given (key, element) pair to the :class:`Multimap`.

        :param key: the key to associate the element with
        :param element: the element to add to the Multimap
        :returns: :py:const:`None`
        """
        self.multimap[key].append(element)

    def get(self, key: KeyType) -> Optional[List[ValueType]]:
        """
        Retrieves all of the elements associated with the given key in
        the :class:`Multimap`.

        :param key: the key to retrieve
        :returns: A List of all of the elements associated with the key
            in the :class:`Multimap`, or :py:const:`None` if no elements are
            associated with the given key.
        """
        if key in self.multimap:
            return self.multimap[key]
        return None

    def delete(self, key: KeyType) -> None:
        """
        Deletes all of the elements associated with the given key in the
        :class:`Multimap`.

        :param key: the key to delete
        :returns: :py:const:`None`
        """
        if key in self.multimap:
            del self.multimap[key]

    def __iter__(self) -> Iterator[Tuple[KeyType, List[ValueType]]]:
        """
        Returns an iterator over all of the (key, elements) pairs in the
        :class:`Multimap`.

        The elements returned by the iterator are of the form (KeyType, List[ValueType]),
        where List[KeyType] is all of the elements associated with the key
        in the first part of the tuple.

        :returns: an iterator
        """
        return iter(self.multimap.items())
