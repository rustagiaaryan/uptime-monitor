# FILE: app/auth.py

import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate to 72 bytes to match bcrypt limitation
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    # Truncate to 72 bytes due to bcrypt limitation
    password_bytes = password.encode('utf-8')[:72]
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')
