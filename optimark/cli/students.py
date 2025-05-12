import click
from optimark.db import get_connection
from optimark.utils import STUDENT_PREFIXES, generate_user_id, hash_password

@click.group(name="student")
def student_cli():
    pass

@student_cli.command("create")
@click.argument("username")
@click.argument("password")
def create_student(username, password):
    """Create a new student"""
    conn = get_connection()
    id = generate_user_id(username, STUDENT_PREFIXES)
    hash_psw = hash_password(password)
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO students (id,name,password) VALUES (%s,%s,%s)",
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
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id,name,email,enrolled_at FROM students WHERE id=%s", (id,))
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
            cur.execute("""
                SELECT id, name, email,
                       DATE_FORMAT(enrolled_at, '%Y-%m-%d %H:%i:%s') AS enrolled_at
                FROM students
                ORDER BY enrolled_at DESC
            """)
            rows = cur.fetchall()
            if not rows:
                click.echo("No students found.")
                return
            click.echo(f"{'ID':8} {'NAME':20} {'EMAIL':25} {'ENROLLED_AT'}")
            click.echo("-" * 70)
            for r in rows:
                click.echo(f"{r['id']:8} {r['name'][:20]:20} { (r['email'] or ''):25} {r['enrolled_at']}")
    finally:
        conn.close()

@student_cli.command("update")
@click.argument("id")
@click.option("--name", help="Update Student Username")
@click.option("--email", help="Update Student Email")
@click.option("--password", help="Update Student Password")
def update_student(id, name, email, password):
    """
    Update student fields.
    --name     : change full name
    --email    : change email (must remain unique)
    --password : change password
    """
    fields, params = [], []
    if name:
        fields.append("name=%s")
        params.append(name)
    if email:
        fields.append("email=%s")
        params.append(email)
    if password:
        fields.append("password=%s")
        params.append(password)
    if not fields:
        return click.echo("Nothing to update. Use --name/--email/--password.")
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
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM students WHERE id=%s", (id,))
        conn.commit()
        click.echo(f"Student {id} deleted.")
    finally:
        conn.close()
