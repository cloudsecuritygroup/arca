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

from ..serializers import Serializer, PickleSerializer
from ..symmetric_encryption import (
    SymmetricEncryptionScheme,
    SimpleSymmetricEncryptionScheme,
)
from ..hash_functions import HashFunctionScheme, SimpleHashFunctionScheme

from .multimap import Multimap
from .emm import EMM

from typing import Dict, Generic, List, TypeVar

import pickle
import os
import enum

from dataclasses import dataclass


MMKeyType = TypeVar("MMKeyType")
MMValueType = TypeVar("MMValueType")


class PiBaseEMMKeyPurpose(enum.IntEnum):
    """
    Internal class denoting the purpose of a key; used to consistently
    derive the same key in operations.
    """

    #: Purpose for a key used for HMAC operations.
    HMAC = 0

    #: Purpose for a key used for encryption operations.
    ENCRYPT = 1


@dataclass(frozen=True)
class PiBaseEMM(
    EMM[bytes, Dict[bytes, bytes], MMKeyType, MMValueType],
    Generic[MMKeyType, MMValueType],
):
    """
    Implements the Pi_bas scheme from [CJJJKRS14].
    """

    mm_key_serializer: Serializer[MMKeyType] = PickleSerializer()
    mm_value_serializer: Serializer[MMValueType] = PickleSerializer()
    encryption_scheme: SymmetricEncryptionScheme = SimpleSymmetricEncryptionScheme()
    hashing_scheme: HashFunctionScheme = SimpleHashFunctionScheme()
    key_length: int = 16

    def generate_key(self) -> bytes:
        return bytes(os.urandom(self.key_length * 2))

    def encrypt(
        self, key: bytes, plaintext_mm: Multimap[MMKeyType, MMValueType]
    ) -> bytes:
        hmac_key = self.__derive_key_for_purpose(key, PiBaseEMMKeyPurpose.HMAC)
        symmetric_key = self.__derive_key_for_purpose(key, PiBaseEMMKeyPurpose.ENCRYPT)

        encrypted_ds = {}
        for keyword, values in plaintext_mm:
            token = self.hashing_scheme.hmac(
                hmac_key, self.mm_key_serializer.save(keyword)
            )
            for index, value in enumerate(values):
                ct_label = self.hashing_scheme.hash(token + bytes(index))
                ct_value = self.encryption_scheme.encrypt(
                    symmetric_key, self.mm_value_serializer.save(value)
                )
                encrypted_ds[ct_label] = ct_value

        return pickle.dumps(encrypted_ds)

    def load_eds(self, eds_bytes: bytes) -> Dict[bytes, bytes]:
        eds: Dict[bytes, bytes] = pickle.loads(eds_bytes)
        return eds

    def token(self, key: bytes, keyword: MMKeyType) -> bytes:
        hmac_key = self.__derive_key_for_purpose(key, PiBaseEMMKeyPurpose.HMAC)
        return self.hashing_scheme.hmac(hmac_key, self.mm_key_serializer.save(keyword))

    def query(self, token: bytes, eds: Dict[bytes, bytes]) -> bytes:
        results: List[bytes] = []

        # Iterate until we can't find any more records:
        index = 0
        while True:
            ct_label = self.hashing_scheme.hash(token + bytes(index))
            if ct_label not in eds:
                break
            results.append(eds[ct_label])
            index += 1

        return pickle.dumps(results)

    def resolve(self, key: bytes, response: bytes) -> List[MMValueType]:
        symmetric_key = self.__derive_key_for_purpose(key, PiBaseEMMKeyPurpose.ENCRYPT)

        unserialized_response: List[bytes] = pickle.loads(response)
        pt_values: List[MMValueType] = []
        for ct_value in unserialized_response:
            pt_value = self.encryption_scheme.decrypt(symmetric_key, ct_value)
            unserialized_value: MMValueType = self.mm_value_serializer.load(pt_value)
            pt_values.append(unserialized_value)

        return pt_values

    def __derive_key_for_purpose(
        self, base_key: bytes, purpose: PiBaseEMMKeyPurpose
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
