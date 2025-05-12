from db import get_connection
import click
import secrets
import hashlib
import string

@click.group(name="student")
def student_cli():
    """Manage students"""
    pass

def generate_user_id(username: str) -> str:
    """Generates 8 bits user_id using username"""
    STUDENT_PREFIXES = ['A','B','E','H']
    salt = secrets.token_hex(2)
    name_bytes = f"{username}{salt}".encode('utf-8')
    prefix = STUDENT_PREFIXES[hashlib.sha1(name_bytes).digest()[0] % len(STUDENT_PREFIXES)]
    
    num = int(hashlib.md5(name_bytes).hexdigest(), 16) % 1_000_000
    middle = f"{num:06d}"

    idx = int(hashlib.sha256(name_bytes).hexdigest(), 16) % 26
    last = string.ascii_uppercase[idx]
    
    if last == prefix:
        last = string.ascii_uppercase[(idx + 1) % 26]

    return f"{prefix}{middle}{last}"

@student_cli.command("create")
@click.argument("id")
@click.argument("name")
@click.argument("password")
def create_student(username, password):
    """Create a new student"""
    conn = get_connection()
    id = generate_user_id(username)
    hash_psw = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO students (id,name,password) VALUES (%s,%s,%s)",
                (id, username, hash_psw)
            )
        conn.commit()
        click.echo(f"Student {id} created.")
    except Exception as e:
        click.echo(f"Error: {e}")
    finally:
        conn.close()

@student_cli.command("get")
@click.argument("id")
def get_student(id):
    """Get student by ID"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id,name,email,enrolled" \
            "_at FROM students WHERE id=%s", (id,))
            r = cur.fetchone()
            click.echo(r or f"No student {id}")
    finally:
        conn.close()

@student_cli.command("list")
def list_students():
    """List all students"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email, enrolled_at FROM students")
            for r in cur.fetchall():
                click.echo(r)
    finally:
        conn.close()

@student_cli.command("update")
@click.argument("id")
@click.option("--email", help="New email")
@click.option("--password", help="New password")
def update_student(id, email, password):
    """Update student's email or password"""
    fields, params = [], []
    if email:
        fields.append("email=%s"); params.append(email)
    if password:
        fields.append("password=%s"); params.append(password)
    if not fields:
        return click.echo("Nothing to update.")
    params.append(id)
    sql = f"UPDATE students SET {', '.join(fields)}, updated_at=NOW() WHERE id=%s"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()
        click.echo(f"Student {id} updated.")
    finally:
        conn.close()

@student_cli.command("delete")
@click.argument("id")
def delete_student(id):
    """Delete a student"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM students WHERE id=%s", (id,))
        conn.commit()
        click.echo(f"Student {id} deleted.")
    finally:
        conn.close()
