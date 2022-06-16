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

from __future__ import annotations

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, hmac, serialization, constant_time
from cryptography.hazmat.primitives import padding as sym_padding

from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric import RSAPublicKey, RSAPrivateKey

import os


def AsymmetricKeyGen() -> Tuple[RSAPublicKey, RSAPrivateKey]:
    """
    Generates a public-key pair for asymmetric encryption purposes.
    Params: None
    Returns: (Public) Asymmetric Encryption Key, (Private) Asymmetric Decryption Key
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    return public_key, private_key


def AsymmetricSerializePublicKey(public_key: RSAPublicKey) -> bytes:
    public_key_bytes: bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return public_key_bytes


def AsymmetricSerializePrivateKey(private_key: RSAPrivateKey) -> bytes:
    private_key_bytes: bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return private_key_bytes


def AsymmetricLoadPublicKey(public_bytes: bytes) -> RSAPublicKey:
    return serialization.load_pem_public_key(public_bytes)


def AsymmetricLoadPrivateKey(private_bytes: bytes) -> RSAPrivateKey:
    return serialization.load_pem_private_key(
        private_bytes,
        password=None,
    )


def AsymmetricEncrypt(public_key: RSAPublicKey, plaintext: bytes) -> bytes:
    """
    Using the public key, encrypt the plaintext
    Params:
       > PublicKey - AsmPublicKey
       > plaintext - bytes
    Returns: ciphertext bytes
    """
    c_bytes: bytes = public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA512()),
            algorithm=hashes.SHA512(),
            label=None,
        ),
    )
    return c_bytes


def AsymmetricDecrypt(private_key: RSAPrivateKey, ciphertext: bytes) -> bytes:
    """
    Using the private key, decrypt the ciphertext
    Params:
       > PrivateKey - AsmPrivateKey
       > ciphertext - bytes
    Returns: paintext (bytes)
    """
    plaintext: bytes = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA512()),
            algorithm=hashes.SHA512(),
            label=None,
        ),
    )
    return plaintext


def SignatureKeyGen() -> Tuple[RSAPublicKey, RSAPrivateKey]:
    """
    Generates a public-key pair for digital signature purposes.
    Params: None
    Returns: (Public) Verifying Key, (Private) Signing Key
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    return public_key, private_key


def SignatureSign(private_key: RSAPrivateKey, data: bytes) -> bytes:
    """
    Uses the private key key to sign the data.
    Params:
        > private_key - SignatureSignKey
        > data       - bytes
    Returns: signature (bytes)
    """
    signature: bytes = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA512()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA512(),
    )
    return signature


def SignatureVerify(public_key: RSAPublicKey, data: bytes, signature: bytes) -> bool:
    """
    Uses the public key key to verify that signature is a valid signature for message.
    Params:
        > PublicKey - AsmPublicKey
        > data      - bytes
        > signature - bytes
    Returns: boolean conditional on signature matches
    """
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA512(),
        )
    except Exception:
        return False

    return True


def Hash(data: bytes) -> bytes:
    """
    Computes a cryptographically secure hash of data.

    :param data:
    :return: the SHA512 hash of the input data
    """
    digest = hashes.Hash(hashes.SHA512())
    digest.update(data)
    return digest.finalize()


def HMAC(key: bytes, data: bytes) -> bytes:
    """
    Compute a SHA-512 hash-based message authentication code (HMAC) of data.
    Returns an error if key is not 128 bits (16 bytes).

    You should use this function if you want a “keyed hash” instead of simply calling Hash
    on the concatenation of key and data, since in practical applications,
    doing a simple concatenation can allow the adversary to retrieve the full key.

    :param key:
    :param data:
    :return: SHA-512 hash-based message authentication code (HMAC) of data (bytes)
    """
    h = hmac.HMAC(key, hashes.SHA512())
    h.update(data)
    return h.finalize()


def SymmetricEncrypt(key: bytes, plaintext: bytes) -> bytes:
    """
    Encrypt the plaintext using AES-CBC mode with the provided key and IV.
    Pads plaintext using 128 bit blocks. Requires a valid size key.
    The ciphertext at the end will inlcude the IV as the last 16 bytes.

    :param key:
    :param plaintext:
    :return: A ciphertext using AES-CBC mode with the provided key and IV (bytes)
    """
    padder = sym_padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext) + padder.finalize()

    iv = SecureRandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return iv + ciphertext


def SymmetricDecrypt(key: bytes, ciphertext: bytes) -> bytes:
    """
    Decrypt the ciphertext using the key. The last 16 bytes of the ciphertext should be the IV.

    :param key:
    :param iv:
    :param ciphertext:
    :return: A plaintext, decrypted from the given ciphertext, key and iv (bytes).
             If the padding in wrong after decryption (which will happen if the wrong key is used),
             then the decryption will be returned with the incorrect padding.
    """
    iv = ciphertext[:16]
    ciphertext = ciphertext[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = sym_padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(plaintext) + unpadder.finalize()
    return plaintext


def SecureRandom(num_bytes: int) -> bytes:
    """
    Given a length, return that many randomly generated bytes. Can be used for an IV or symmetric key.

    :param num_bytes:
    :return: num_bytes random bytes
    """
    return os.urandom(num_bytes)


def HashKDF(key: bytes, purpose: str) -> bytes:
    """
    Takes a key and a purpose and returns a new key.
    HashKDF is a keyed hash function that can generate multiple keys from a single key.
    This can simplify your key management schemes.

    Note that the "purpose" adds another input the the hash function such that the same password can produce
    more than one key.

    :param key:
    :param purpose:
    :return: a new key
    """
    hkdf = HKDF(
        algorithm=hashes.SHA512(),
        length=len(key),
        salt=None,
        info=purpose.encode(),
    )
    key = hkdf.derive(key)
    return key


def HashKDFBytes(key: bytes, purpose: bytes) -> bytes:
    """
    Takes a key and a purpose and returns a new key.
    HashKDF is a keyed hash function that can generate multiple keys from a single key.
    This can simplify your key management schemes.

    Note that the "purpose" adds another input the the hash function such that the same password can produce
    more than one key.

    :param key:
    :param purpose:
    :return: a new key
    """
    hkdf = HKDF(
        algorithm=hashes.SHA512(),
        length=len(key),
        salt=None,
        info=purpose,
    )
    key = hkdf.derive(key)
    return key
