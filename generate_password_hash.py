"""Script auxiliar para generar hashes de contraseñas para WareFlow WMS."""

import hashlib
import hmac
import os

_ITERATIONS = 100_000
_SALT_SIZE = 16
_ALGORITHM = "sha256"


def hash_password(password: str) -> str:
    """Genera un hash de contraseña usando PBKDF2-SHA256."""
    salt = os.urandom(_SALT_SIZE)
    pwd_hash = hashlib.pbkdf2_hmac(_ALGORITHM, password.encode("utf-8"), salt, _ITERATIONS)
    return f"{_ITERATIONS}${salt.hex()}${pwd_hash.hex()}"


if __name__ == "__main__":
    # Generar hash para admin123
    password = "admin123"
    hash_result = hash_password(password)
    print(f"Hash para '{password}':")
    print(hash_result)
    print("\nUsa este hash en seed_data.sql")
