import click
from datetime import datetime
from pymysql.err import IntegrityError
from optimark.utils import generate_exam_id

from optimark.db import get_connection

@click.group("exam")
def exam_cli():
    pass

@click.command("create")
@click.argument("course_code")
@click.argument("semester_id")
@click.argument("name")
@click.option("--start-at", default=None, help="Exam start time")
def create_exam(course_code, semester_id, name, start_time):
    """
    COURSE_CODE  : course code (FK to courses.code)  
    SEMESTER_ID  : semester ID (FK to semesters.id)  
    NAME         : exam name  
    --start-at : optional start datetime  
    """
    dt = None
    if start_time:
        try:
            dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return click.echo("Invalid --start-time format, use YYYY-MM-DD HH:MM:SS")
    exam_id = generate_exam_id(course_code, semester_id, name)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                    INSERT INTO exams (id, course_code, semester_id, name, start_time)
                    VALUES (%s, %s, %s, %s, %s)
                """, (exam_id, course_code, semester_id, name, dt)
            )
        conn.commit()
        click.echo(f"{course_code} {semester_id} {name}({exam_id}) created.")
    except IntegrityError as ie:
        click.echo(f"Could not create exam ({ie})")
    finally:
        conn.close()

@exam_cli.command("list")
def list_exams():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, course_code, semester_id, name,
                       DATE_FORMAT(start_time, '%%Y-%%m-%%d %%H:%%i:%%s') AS start_time,
                       DATE_FORMAT(created_at, '%%Y-%%m-%%d %%H:%%i:%%s') AS created_at
                FROM exams
                ORDER BY created_at DESC
            """)
            rows = cur.fetchall()
            if not rows:
                return click.echo("No exams found.")
            click.echo(f"{'ID':8} {'COURSE':12} {'SEM':6} {'NAME':20} {'START':19} {'CREATED_AT'}")
            click.echo("-" * 80)
            for r in rows:
                click.echo(
                    f"{r['id']:8} {r['course_code']:12} {r['semester_id']:6} "
                    f"{r['name'][:20]:20} {r['start_time']:19} {r['created_at']}"
                )
    finally:
        conn.close()

@exam_cli.command("get")
@click.argument("course_code")
@click.argument("semester_id")
def get_exam(course_code, semester_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT * FROM exams 
                        WHERE course_code=%s
                          AND semester_id=%s
                        """, (course_code, semester_id,))
            r = cur.fetchone()
            if not r:
                return click.echo(f"No {course_code} exam created in {semester_id}!")
            click.echo(r)
    finally:
        conn.close()

@exam_cli.command("update")
@click.argument("exam_id")
@click.option("--name", help="New exam name")
@click.option("--start-at", help="New start time")
def update_exam(exam_id, name, start_time):
    fields, params = [], []
    if name:
        fields.append("name=%s")
        params.append(name)
    if start_time:
        try:
            dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return click.echo("Invalid --start-time format, use YYYY-MM-DD HH:MM:SS")
        fields.append("start_time=%s")
        params.append(dt)
    if not fields:
        return click.echo("Nothing to update. Use --name and/or --start-time.")

    params.append(exam_id)
    sql = f"UPDATE exams SET {', '.join(fields)}, updated_at=NOW() WHERE id=%s"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
        conn.commit()
        click.echo(f"✔ Exam {exam_id} updated.")
    finally:
        conn.close()

@exam_cli.command("delete")
@click.argument("exam_id")
def delete_exam(exam_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM exams WHERE id=%s", (exam_id,))
        conn.commit()
        click.echo(f"✔ Exam {exam_id} deleted.")
    finally:
        conn.close()