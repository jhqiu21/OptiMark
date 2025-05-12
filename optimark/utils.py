import hashlib
import secrets
import string

STAFF_PREFIXES = ['S','P','M']
STUDENT_PREFIXES = ['A','B','E','H']

def generate_user_id(username: str, prefixs) -> str:
    """Generates 8 bits user_id using username"""
    salt = secrets.token_hex(2)
    name_bytes = f"{username}{salt}".encode('utf-8')
    prefix = prefixs[hashlib.sha1(name_bytes).digest()[0] % len(prefixs)]

    num = int(hashlib.md5(name_bytes).hexdigest(), 16) % 1_000_000
    middle = f"{num:06d}"

    idx = int(hashlib.sha256(name_bytes).hexdigest(), 16) % 26
    last = string.ascii_uppercase[idx]
    
    if last == prefix:
        last = string.ascii_uppercase[(idx + 1) % 26]

    return f"{prefix}{middle}{last}"

def hash_password(password: str):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
