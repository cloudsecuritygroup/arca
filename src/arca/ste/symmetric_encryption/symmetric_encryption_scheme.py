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


class SymmetricEncryptionScheme(ABC):
    """
    A :class:`SymmetricEncryptionScheme` is a interface used to
    pass specific symmetric encryption schemes to other cryptographic
    objects, such as an :class:`EncryptedMultimapScheme`.
    """

    @abstractmethod
    def encrypt(self, key: bytes, plaintext: bytes) -> bytes:
        """
        Encrypts a plaintext bytestring with the given key.

        :param key: the key to encrypt with
        :param plaintext: the plaintext to encrypt
        :return: the ciphertext
        """
        ...

    @abstractmethod
    def decrypt(self, key: bytes, plaintext: bytes) -> bytes:
        """
        Decrypts a ciphertext previously encrypted with the given key in
        a call to :func:`encrypt`.

        :param key: the key to decrypt with
        :param ciphertext: the ciphertext to decrypt
        :return: bytes representing a key
        """
        ...
