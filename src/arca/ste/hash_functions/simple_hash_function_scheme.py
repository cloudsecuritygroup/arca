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

from .hash_function_scheme import HashFunctionScheme
from ... import crypto


class SimpleHashFunctionScheme(HashFunctionScheme):
    """
    A simple hash function scheme using primitives from the simple crypto
    module. Implements the :class:`HashFunctionScheme` interface.
    """

    def hash(self, plaintext: bytes) -> bytes:
        return crypto.Hash(plaintext)

    def hmac(self, key: bytes, plaintext: bytes) -> bytes:
        return crypto.HMAC(key, plaintext)
