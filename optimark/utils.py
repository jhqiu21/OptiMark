from datetime import datetime, date
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


def compute_semester_id(start_date: str) -> str:
    dt = datetime.strptime(start_date, "%Y-%m-%d").date()
    year = dt.year
    yy   = year % 100

    if dt.month >= 8:
        sem = "S1"
        yy_next = (year + 1) % 100
        sem_id = f"{yy:02d}{yy_next:02d}{sem}"
        start = date(year, 8, 1)
        end = date(year, 12, 31)
    elif dt.month <= 4:
        sem = "S2"
        yy_prev = (year - 1) % 100
        sem_id = f"{yy_prev:02d}{yy:02d}{sem}"
        start = date(year, 1, 1)
        end = date(year, 4, 30)
    else:
        sem = "S3"
        yy_prev = (year - 1) % 100
        sem_id = f"{yy_prev:02d}{yy:02d}{sem}"
        start = date(year, 5, 1)
        end = date(year, 7, 31)

    return sem_id, start.isoformat(), end.isoformat()