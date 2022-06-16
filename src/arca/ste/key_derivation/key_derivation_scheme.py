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


class KeyDerivationScheme(ABC):
    """
    An interface representing a key derivation scheme.
    """

    @abstractmethod
    def hkdf(self, base_key: bytes, purpose: bytes) -> bytes:
        """
        Derives a key from base_key for the given human-readable
        purpose.

        :param key: the key to derive from
        :param purpose: the purpose of the new key
        :return: a byte string representing the derived key
        """
        ...
