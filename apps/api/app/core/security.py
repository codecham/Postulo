from pwdlib import PasswordHash

# Argon2: the current recommended algorithm for password hashing
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Return a salted hash of the password, safe to store in the database."""
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Check a plain password against a stored hash."""
    return password_hash.verify(password, hashed_password)
