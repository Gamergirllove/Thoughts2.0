import os
from cryptography.fernet import Fernet, InvalidToken

KEY_ENV = "HOME_STORAGE_KEY"


def generate_key() -> str:
    return Fernet.generate_key().decode()


def _get_fernet() -> Fernet:
    raw = os.environ.get(KEY_ENV)
    if not raw:
        raise RuntimeError(
            f"{KEY_ENV} is not set. Generate one with: "
            "python -c \"from crypto_utils import generate_key; print(generate_key())\" "
            "and set it as an env var on the app (NOT on the home storage server)."
        )
    return Fernet(raw.encode())


def encrypt_bytes(data: bytes) -> bytes:
    return _get_fernet().encrypt(data)


def decrypt_bytes(data: bytes) -> bytes:
    try:
        return _get_fernet().decrypt(data)
    except InvalidToken:
        raise RuntimeError(
            "Could not decrypt data from home storage — wrong HOME_STORAGE_KEY, "
            "or the stored bytes are not encrypted with this key."
        )


def key_configured() -> bool:
    return bool(os.environ.get(KEY_ENV))
