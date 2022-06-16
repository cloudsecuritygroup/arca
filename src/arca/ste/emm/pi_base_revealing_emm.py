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
from ..key_derivation import KeyDerivationScheme, SimpleKeyDerivationScheme

from .multimap import Multimap
from .revealing_emm import RevealingEMM

from typing import Dict, Generic, List, TypeVar

import pickle
import os

from dataclasses import dataclass


MMKeyType = TypeVar("MMKeyType")
MMValueType = TypeVar("MMValueType")


@dataclass(frozen=True)
class PiBaseRevealingEMM(
    RevealingEMM[bytes, Dict[bytes, bytes], MMKeyType, MMValueType],
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
    key_derivation_scheme: KeyDerivationScheme = SimpleKeyDerivationScheme()

    def generate_key(self) -> bytes:
        return bytes(os.urandom(self.key_length))

    def encrypt(
        self, key: bytes, plaintext_mm: Multimap[MMKeyType, MMValueType]
    ) -> bytes:
        encrypted_ds = {}
        for keyword, values in plaintext_mm:
            token = self.token(key, keyword)
            for index, value in enumerate(values):
                ct_label = self.key_derivation_scheme.hkdf(token, bytes(index))
                symmetric_key = self.key_derivation_scheme.hkdf(token, "value".encode())
                ct_value = self.encryption_scheme.encrypt(
                    symmetric_key, self.mm_value_serializer.save(value)
                )
                encrypted_ds[ct_label] = ct_value

        return pickle.dumps(encrypted_ds)

    def load_eds(self, eds_bytes: bytes) -> Dict[bytes, bytes]:
        eds: Dict[bytes, bytes] = pickle.loads(eds_bytes)
        return eds

    def token(self, key: bytes, keyword: MMKeyType) -> bytes:
        return self.key_derivation_scheme.hkdf(
            key,
            self.mm_key_serializer.save(keyword),
        )

    def query(self, token: bytes, eds: Dict[bytes, bytes]) -> List[MMValueType]:
        results: List[bytes] = []

        # Iterate until we can't find any more records:
        index = 0
        while True:
            ct_label = self.key_derivation_scheme.hkdf(token, bytes(index))
            if ct_label not in eds:
                break
            symmetric_key = self.key_derivation_scheme.hkdf(token, "value".encode())
            print(eds[ct_label])
            results.append(self.encryption_scheme.decrypt(symmetric_key, eds[ct_label]))
            index += 1

        pt_values: List[MMValueType] = []
        for pt_value in results:
            unserialized_value: MMValueType = self.mm_value_serializer.load(pt_value)
            pt_values.append(unserialized_value)

        return pt_values
