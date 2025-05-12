import click
from optimark.db import get_connection
from optimark.utils import STAFF_PREFIXES, generate_user_id, hash_password

@click.group(name="staff")
def staff_cli():
    pass

@staff_cli.command("create")
@click.argument("username")
@click.argument("password")
@click.option("--email", help="Email address (optional)", default=None)
def create_staff(username, password, email):
    """
    Create a new staff member.
    ID       : 8-char staff ID
    NAME     : full name
    PASSWORD : raw password
    --email  : optional email (must be unique if provided)
    """
    id = generate_user_id(username, STAFF_PREFIXES)
    pwd_hash = hash_password(password)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO staff (id, name, email, password)
                VALUES (%s, %s, %s, %s)
            """, (id, username, email, pwd_hash))
        conn.commit()
        click.echo(f"Staff {username}({id}) created.")
    except Exception as e:
        click.echo(f"Error creating staff: {e}")
    finally:
        conn.close()

@staff_cli.command("get")
@click.argument("id")
def get_staff(id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, email,
                       DATE_FORMAT(enrolled_at, '%%Y-%%m-%%d') AS created_at,
                       DATE_FORMAT(updated_at, '%%Y-%%m-%%d') AS updated_at
                FROM staff
                WHERE id=%s
            """, (id,))
            staff = cur.fetchone()
            if staff:
                click.echo(staff)
            else:
                click.echo(f"No staff found with id {id}")
    finally:
        conn.close()

@staff_cli.command("list")
def list_staff():
    """List all staff members."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, email,
                       DATE_FORMAT(enrolled_at, '%Y-%m-%d %H:%i:%s') AS enrolled_at
                FROM staff
                ORDER BY enrolled_at DESC
            """)
            rows = cur.fetchall()
            if not rows:
                click.echo("No staff found.")
                return
            click.echo(f"{'ID':8} {'NAME':20} {'EMAIL':25} {'ENROLLED_AT'}")
            click.echo("-" * 70)
            for r in rows:
                click.echo(f"{r['id']:8} {r['name'][:20]:20} { (r['email'] or ''):25} {r['enrolled_at']}")
    finally:
        conn.close()

@staff_cli.command("update")
@click.argument("id")
@click.option("--name", help="Update Staff Username")
@click.option("--email", help="Update Staff Email")
@click.option("--password", help="Update Staff Password")
def update_staff(id, name, email, password):
    """
    Update staff fields.
    --name     : change full name
    --email    : change email (must remain unique)
    --password : change password
    """
    fields, params = [], []
    if name:
        fields.append("name=%s")
        params.append(name)
    if email is not None:  # allow empty string?
        fields.append("email=%s")
        params.append(email)
    if password:
        fields.append("password=%s")
        params.append(hash_password(password))
    if not fields:
        return click.echo("Nothing to update. Use --name/--email/--password.")

    params.append(id)
    sql = f"UPDATE staff SET {', '.join(fields)}, updated_at=NOW() WHERE id=%s"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
        conn.commit()
        click.echo(f"Staff {id} updated.")
    finally:
        conn.close()

@staff_cli.command("delete")
@click.argument("id")
def delete_staff(id):
    """Delete a staff member (and related offerings will be cascaded)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM staff WHERE id=%s", (id,))
        conn.commit()
        click.echo(f"Staff {id} deleted.")
    finally:
        conn.close()
