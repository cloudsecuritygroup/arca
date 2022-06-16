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

from .symmetric_encryption_scheme import SymmetricEncryptionScheme

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

import os

IV_LENGTH = 16


class AesSymmetricEncryptionScheme(SymmetricEncryptionScheme):
    """
    A symmetric encryption scheme based on AES. Implements the
    :class:`SymmetricEncryptionScheme` interface.
    """

    def encrypt(self, key: bytes, plaintext: bytes) -> bytes:
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext)
        padded_data = padder.finalize()

        iv = os.urandom(IV_LENGTH)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return iv + ciphertext

    def decrypt(self, key: bytes, ciphertext: bytes) -> bytes:
        iv = ciphertext[:IV_LENGTH]
        ciphertext = ciphertext[IV_LENGTH:]

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(plaintext) + unpadder.finalize()
        return plaintext
