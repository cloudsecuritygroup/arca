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

from abc import ABC, abstractmethod

from typing import Generic, TypeVar

T = TypeVar("T")


class Serializer(ABC, Generic[T]):
    """
    Serializes a particular data type T. Used to allow users to specify
    how items are serialized prior to storing them in an encrypted data
    structure.
    """

    @abstractmethod
    def save(self, value: T) -> bytes:
        """
        Serializes the given value into a byte string.

        :param value: the value to serialize
        :return: the value in serialized form
        """
        ...

    @abstractmethod
    def load(self, blob: bytes) -> T:
        """
        Restores the value of type T from the given blob.

        :param blob: the byte string to deserialize, as previously
            generated from :func:`save`
        :return: the original value
        """
        ...
