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

import unittest


from arca.ste.emm import PiBaseEMM, Multimap
from arca.ste.symmetric_encryption import AesSymmetricEncryptionScheme


class TestPiBaseEMM(unittest.TestCase):
    def test_pi_base_emm_query_existing_keys(self) -> None:
        plaintext_mm: Multimap[str, int] = Multimap()
        plaintext_mm.set("a", 1)
        plaintext_mm.set("a", 2)
        plaintext_mm.set("a", 3)
        plaintext_mm.set("b", 4)
        plaintext_mm.set("c", 5)
        plaintext_mm.set("c", 1)
        plaintext_mm.set("c", 2)
        plaintext_mm.set("c", 3)
        plaintext_mm.set("d", 4)
        plaintext_mm.set("d", 5)

        pi_base: PiBaseEMM[str, int] = PiBaseEMM()

        key = pi_base.generate_key()
        eds = pi_base.load_eds(pi_base.encrypt(key, plaintext_mm))

        for plaintext_key, _ in plaintext_mm:
            token = pi_base.token(key, plaintext_key)
            response = pi_base.query(token, eds)
            self.assertCountEqual(
                pi_base.resolve(key, response), plaintext_mm.get(plaintext_key)
            )

    def test_pi_base_emm_query_nonexistent_key(self) -> None:
        plaintext_mm: Multimap[str, int] = Multimap()
        plaintext_mm.set("a", 1)
        plaintext_mm.set("a", 2)
        plaintext_mm.set("a", 3)

        pi_base: PiBaseEMM[str, int] = PiBaseEMM()

        key = pi_base.generate_key()
        eds = pi_base.load_eds(pi_base.encrypt(key, plaintext_mm))

        token = pi_base.token(key, "non-existent")
        response = pi_base.query(token, eds)
        self.assertEqual(pi_base.resolve(key, response), [])

    def test_pi_base_emm_with_different_scheme(self) -> None:
        plaintext_mm: Multimap[str, int] = Multimap()
        plaintext_mm.set("a", 1)
        plaintext_mm.set("a", 2)
        plaintext_mm.set("a", 3)
        plaintext_mm.set("b", 4)
        plaintext_mm.set("c", 5)
        plaintext_mm.set("c", 1)

        pi_base: PiBaseEMM[str, int] = PiBaseEMM(
            encryption_scheme=AesSymmetricEncryptionScheme()
        )

        key = pi_base.generate_key()
        eds = pi_base.load_eds(pi_base.encrypt(key, plaintext_mm))

        for plaintext_key, _ in plaintext_mm:
            token = pi_base.token(key, plaintext_key)
            response = pi_base.query(token, eds)
            self.assertCountEqual(
                pi_base.resolve(key, response), plaintext_mm.get(plaintext_key)
            )
