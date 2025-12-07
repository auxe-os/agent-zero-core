import hashlib
import hmac
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import os


def hash_data(data: str, password: str):
    """Hashes a string using HMAC-SHA256.

    Args:
        data: The string to hash.
        password: The password to use for the HMAC.

    Returns:
        The hashed string.
    """
    return hmac.new(password.encode(), data.encode(), hashlib.sha256).hexdigest()


def verify_data(data: str, hash: str, password: str):
    """Verifies a string against a hash.

    Args:
        data: The string to verify.
        hash: The hash to verify against.
        password: The password to use for the HMAC.

    Returns:
        True if the string is valid, False otherwise.
    """
    return hash_data(data, password) == hash


def _generate_private_key():
    """Generates a new RSA private key."""
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )


def _generate_public_key(private_key: rsa.RSAPrivateKey):
    """Generates a public key from a private key."""
    return (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .hex()
    )
    
def _decode_public_key(public_key: str) -> rsa.RSAPublicKey:
    """Decodes a public key from a hex string."""
    # Decode hex string back to bytes
    pem_bytes = bytes.fromhex(public_key)
    # Load the PEM public key
    key = serialization.load_pem_public_key(pem_bytes)
    if not isinstance(key, rsa.RSAPublicKey):
        raise TypeError("The provided key is not an RSAPublicKey")
    return key

def encrypt_data(data: str, public_key_pem: str):
    """Encrypts data using a public key.

    Args:
        data: The data to encrypt.
        public_key_pem: The public key in PEM format.

    Returns:
        The encrypted data as a hex string.
    """
    return _encrypt_data(data.encode("utf-8"), _decode_public_key(public_key_pem))

def _encrypt_data(data: bytes, public_key: rsa.RSAPublicKey):
    """Encrypts data using a public key."""
    b = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return b.hex()

def decrypt_data(data: str, private_key: rsa.RSAPrivateKey):
    """Decrypts data using a private key.

    Args:
        data: The data to decrypt.
        private_key: The private key.

    Returns:
        The decrypted data.
    """
    b = private_key.decrypt(
        bytes.fromhex(data),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return b.decode("utf-8")

