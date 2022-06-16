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

from .edx import EDX
from .simple_edx import SimpleEDX, SimpleEDXKeyPurpose

from typing import Dict, Generic, TypeVar, Tuple, Any
from multiprocessing import Pool
from functools import partial
from tqdm import tqdm

import pickle


DXKeyType = TypeVar("DXKeyType")
DXValueType = TypeVar("DXValueType")


def compute_edx_pair(
    dx_pair: Tuple[DXKeyType, DXValueType],
    *,
    hmac_key: bytes,
    symmetric_key: bytes,
    hashing_scheme: HashFunctionScheme,
    encryption_scheme: SymmetricEncryptionScheme,
    dx_key_serializer: Serializer[DXKeyType],
    dx_value_serializer: Serializer[DXValueType],
) -> Tuple[bytes, bytes]:
    label, value = dx_pair
    ct_label = hashing_scheme.hmac(hmac_key, dx_key_serializer.save(label))
    ct_value = encryption_scheme.encrypt(symmetric_key, dx_value_serializer.save(value))
    return (ct_label, ct_value)


class MultiprocessEDX(
    Generic[DXKeyType, DXValueType],
    SimpleEDX[DXKeyType, DXValueType],
):
    """
    Implements a simple encrypted dictionary scheme based on the Pi_bas
    encrypted multimap scheme from [CJJJKRS14].
    """

    def __init__(self, num_processes: int, **kwargs: Any):
        self.num_processes = num_processes
        super(MultiprocessEDX, self).__init__(**kwargs)

    def encrypt(self, key: bytes, plaintext_dx: Dict[DXKeyType, DXValueType]) -> bytes:
        hmac_key = self._derive_key_for_purpose(key, SimpleEDXKeyPurpose.HMAC)
        symmetric_key = self._derive_key_for_purpose(key, SimpleEDXKeyPurpose.ENCRYPT)

        compute_edx = partial(
            compute_edx_pair,
            hmac_key=hmac_key,
            symmetric_key=symmetric_key,
            hashing_scheme=self.hashing_scheme,
            encryption_scheme=self.encryption_scheme,
            dx_key_serializer=self.dx_key_serializer,
            dx_value_serializer=self.dx_value_serializer,
        )

        print(f"Using {self.num_processes} cores")
        encrypted_ds = {}
        with Pool(self.num_processes) as pool:
            encrypted_ds = dict(
                tqdm(
                    pool.imap(compute_edx, plaintext_dx.items()),
                    total=len(plaintext_dx.items()),
                    leave=False,
                )
            )

        return pickle.dumps(encrypted_ds)
