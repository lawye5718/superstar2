"""Security utilities"""

import bcrypt

# bcrypt enforces a maximum password length of 72 bytes (a hard limit of the algorithm).
# Both hashing and verification truncate to this limit, which matches the behaviour of
# bcrypt 3.x (which silently truncated) while staying compatible with bcrypt 4.x
# (which raises ValueError on overflow instead of truncating).  Because truncation is
# applied consistently in both directions, passwords longer than 72 bytes authenticate
# correctly – only the first 72 bytes are meaningful, which matches standard bcrypt
# semantics.  Production deployments may additionally choose to reject passwords
# longer than 72 bytes at the API validation layer.
_BCRYPT_MAX_BYTES = 72


def _encode_password(password: str) -> bytes:
    """Encode password to bytes, truncated to bcrypt's 72-byte limit."""
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def get_password_hash(password: str) -> str:
    """Generate bcrypt password hash."""
    return bcrypt.hashpw(_encode_password(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(_encode_password(plain_password), hashed_password.encode("utf-8"))