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


class HashFunctionScheme(ABC):
    """
    An interface representing a hash function scheme. The interface is
    intended to capture different usages of the same hash function family.
    """

    @abstractmethod
    def hash(self, plaintext: bytes) -> bytes:
        """
        Computes a hash over the given plaintext.

        :param plaintext: the plaintext to hash
        :return: a hash
        """
        ...

    @abstractmethod
    def hmac(self, key: bytes, plaintext: bytes) -> bytes:
        """
        Computes an HMAC (keyed hash) over the given plaintext with the
        given key.

        :param key: the key to use
        :param plaintext: the plaintext to compute an HMAC over
        :return: an HMAC
        """
        ...
