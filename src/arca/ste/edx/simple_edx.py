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

from ..serializers import Serializer, PickleSerializer, NoneSerializer
from ..symmetric_encryption import (
    SymmetricEncryptionScheme,
    SimpleSymmetricEncryptionScheme,
)
from ..hash_functions import HashFunctionScheme, SimpleHashFunctionScheme

from .edx import EDX

from typing import Dict, Generic, Optional, TypeVar
from dataclasses import dataclass
from tqdm import tqdm

import pickle
import os
import enum


DXKeyType = TypeVar("DXKeyType")
DXValueType = TypeVar("DXValueType")


class SimpleEDXKeyPurpose(enum.IntEnum):
    """
    Internal class denoting the purpose of a key; used to consistently
    derive the same key in operations.
    """

    """
    Purpose for a key used for HMAC operations.
    """
    HMAC = 0

    """
    Purpose for a key used for encryption operations.
    """
    ENCRYPT = 1


@dataclass(frozen=True)
class SimpleEDX(
    EDX[bytes, Dict[bytes, bytes], DXKeyType, DXValueType],
    Generic[DXKeyType, DXValueType],
):
    """
    Implements a simple encrypted dictionary scheme based on the Pi_bas
    encrypted multimap scheme from [CJJJKRS14].
    """

    dx_key_serializer: Serializer[DXKeyType] = PickleSerializer()
    dx_value_serializer: Serializer[DXValueType] = PickleSerializer()
    encryption_scheme: SymmetricEncryptionScheme = SimpleSymmetricEncryptionScheme()
    hashing_scheme: HashFunctionScheme = SimpleHashFunctionScheme()
    key_length: int = 16

    def generate_key(self) -> bytes:
        return bytes(os.urandom(self.key_length * 2))

    def encrypt(self, key: bytes, plaintext_dx: Dict[DXKeyType, DXValueType]) -> bytes:
        hmac_key = self._derive_key_for_purpose(key, SimpleEDXKeyPurpose.HMAC)
        symmetric_key = self._derive_key_for_purpose(key, SimpleEDXKeyPurpose.ENCRYPT)

        encrypted_ds = {}
        for label, value in tqdm(plaintext_dx.items(), leave=False):
            ct_label = self.hashing_scheme.hmac(
                hmac_key, self.dx_key_serializer.save(label)
            )
            ct_value = self.encryption_scheme.encrypt(
                symmetric_key, self.dx_value_serializer.save(value)
            )
            encrypted_ds[ct_label] = ct_value

        return pickle.dumps(encrypted_ds)

    def load_eds(self, eds_bytes: bytes) -> Dict[bytes, bytes]:
        eds: Dict[bytes, bytes] = pickle.loads(eds_bytes)
        return eds

    def token(self, key: bytes, keyword: DXKeyType) -> bytes:
        hmac_key = self._derive_key_for_purpose(key, SimpleEDXKeyPurpose.HMAC)
        return self.hashing_scheme.hmac(hmac_key, self.dx_key_serializer.save(keyword))

    def query(self, token: bytes, eds: Dict[bytes, bytes]) -> Optional[bytes]:
        if token not in eds:
            return None
        return eds[token]

    def resolve(self, key: bytes, response: bytes) -> DXValueType:
        symmetric_key = self._derive_key_for_purpose(key, SimpleEDXKeyPurpose.ENCRYPT)

        pt_value = self.encryption_scheme.decrypt(symmetric_key, response)
        unserialized_value: DXValueType = self.dx_value_serializer.load(pt_value)
        return unserialized_value

    def _derive_key_for_purpose(
        self, base_key: bytes, purpose: SimpleEDXKeyPurpose
    ) -> bytes:
        """
        Derives a key for the given purpose. Used internally as an extremely
        minor optimization over using a HKDF (which can add up during
        repeated calls to :func:`token`) in exchange for additional key
        material created in :func:`generate_key`.

        :param base_key: the key generated in :func:`generate_key`
        :param purpose: the purpose of the key to be derived
        :return: the key for the specified purpose
        """
        start = self.key_length * purpose.value
        end = start + self.key_length
        return base_key[start:end]
