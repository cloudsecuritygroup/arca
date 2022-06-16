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
from ..key_derivation import KeyDerivationScheme, SimpleKeyDerivationScheme
from ..hash_functions import HashFunctionScheme, SimpleHashFunctionScheme

from .revealing_edx import RevealingEDX

from typing import Dict, Generic, Optional, TypeVar
from dataclasses import dataclass
from tqdm import tqdm

import pickle
import os


DXKeyType = TypeVar("DXKeyType")
DXValueType = TypeVar("DXValueType")


@dataclass(frozen=True)
class SimpleRevealingEDX(
    RevealingEDX[bytes, Dict[bytes, bytes], DXKeyType, DXValueType],
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
    key_derivation_scheme: KeyDerivationScheme = SimpleKeyDerivationScheme()
    key_length: int = 16

    def generate_key(self) -> bytes:
        return bytes(os.urandom(self.key_length))

    def encrypt(self, key: bytes, plaintext_dx: Dict[DXKeyType, DXValueType]) -> bytes:
        encrypted_ds = {}
        for label, value in tqdm(plaintext_dx.items(), leave=False):
            token = self.token(key, label)

            ct_label = self.key_derivation_scheme.hkdf(token, "hmac".encode())

            symmetric_key = self.key_derivation_scheme.hkdf(token, "value".encode())
            ct_value = self.encryption_scheme.encrypt(
                symmetric_key, self.dx_value_serializer.save(value)
            )
            encrypted_ds[ct_label] = ct_value

        return pickle.dumps(encrypted_ds)

    def load_eds(self, eds_bytes: bytes) -> Dict[bytes, bytes]:
        eds: Dict[bytes, bytes] = pickle.loads(eds_bytes)
        return eds

    def token(self, key: bytes, keyword: DXKeyType) -> bytes:
        return self.key_derivation_scheme.hkdf(
            key,
            self.dx_key_serializer.save(keyword),
        )

    def query(self, token: bytes, eds: Dict[bytes, bytes]) -> Optional[DXValueType]:
        ct_label = self.key_derivation_scheme.hkdf(token, "hmac".encode())
        if ct_label not in eds:
            return None

        symmetric_key = self.key_derivation_scheme.hkdf(token, "value".encode())
        ciphertext = self.encryption_scheme.decrypt(symmetric_key, eds[ct_label])
        unserialized_value: DXValueType = self.dx_value_serializer.load(ciphertext)
        return unserialized_value
