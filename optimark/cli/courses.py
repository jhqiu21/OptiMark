import click
from optimark.db import get_connection

@click.group("course")
def course_cli():
    pass

@course_cli.command("create")
@click.argument('code')
@click.argument('name')
def create_course(code: str, name: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO courses (code, name) VALUES (%s, %s)", (code, name))
        conn.commit()
        click.echo(f"Course {code}-{name} created.")
    except Exception as e:
        click.echo(f"Error creating course: {e}")
    finally:
        conn.close()

@course_cli.command("delete")
@click.argument('code')
def delete_course(code: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM courses WHERE code=%s", (code,))
        conn.commit()
        click.echo(f"Course {code} deleted.")
    finally:
        conn.close()

@course_cli.command("update")
@click.argument("code")
@click.option("--new_code", help="Update Course Code")
@click.option("--name", help="Update Course Name")
def update_course(code, new_code, name):
    fields, params = [], []
    if new_code:
        fields.append("code=%s")
        params.append(new_code)
    if name:
        fields.append("name=%s")
        params.append(name)
    if not fields:
        return click.echo("Nothing to update. Use --new_code/--name.")

    params.append(code)
    sql = f"UPDATE courses SET {', '.join(fields)} WHERE code=%s"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
        conn.commit()
        click.echo(f"Course {code} updated.")
    finally:
        conn.close()

@course_cli.command("list")
def list_courses():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT code, name FROM courses")
            rows = cur.fetchall()
            if not rows:
                click.echo("No courses found.")
                return
            click.echo(f"{'CODE':12} {'NAME':100}")
            click.echo("-" * 112)
            for r in rows:
                click.echo(f"{r['code']:12} {r['name']:100}")
    finally:
        conn.close()

@course_cli.command("get")
def get_course(code: str) -> str:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT code, name FROM courses WHERE code=%s", (code,))
            course = cur.fetchone()
            if course:
                click.echo(course)
            else:
                click.echo(f"No course found with code {code}")
    finally:
        conn.close()