"""Funciones de hashing y verificación de contraseñas para WareFlow WMS."""

import hashlib
import hmac
import os

_ITERATIONS = 100_000
_SALT_SIZE = 16
_ALGORITHM = "sha256"


def hash_password(password: str) -> str:
    salt = os.urandom(_SALT_SIZE)
    pwd_hash = hashlib.pbkdf2_hmac(_ALGORITHM, password.encode("utf-8"), salt, _ITERATIONS)
    return f"{_ITERATIONS}${salt.hex()}${pwd_hash.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        iterations, salt_hex, hash_hex = stored_hash.split("$")
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        pwd_hash = hashlib.pbkdf2_hmac(_ALGORITHM, password.encode("utf-8"), salt, int(iterations))
        return hmac.compare_digest(pwd_hash, expected_hash)
    except Exception:
        return False
