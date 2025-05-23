import click
from datetime import date as _date
from pymysql.err import IntegrityError

from optimark.db import get_connection
from optimark.utils import compute_semester_id
from optimark.cli.semesters import create_semester
from optimark.cli.courses import create_course, update_course

@click.group("offer")
def offer_cli():
    pass

@offer_cli.command("create")
@click.argument("course_code")
@click.argument("course_name")
@click.option(
    "--date",
    "enrolled_date",
    default=None,
    help="Enrollment date (YYYY-MM-DD). Defaults to today."
)
def create_offer(course_code: str, course_name: str, enrolled_date: str):
    if not enrolled_date:
        enrolled_date = _date.today().isoformat()
    
    sem_id, sem_start, sem_end = compute_semester_id(enrolled_date)
    try:
        create_semester.callback(sem_id, sem_start, sem_end)
    except Exception:
        pass
    try:
        create_course.callback(course_code, course_name)
    except Exception:
        pass
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO offers (course_code, semester_id, enrolled_at) VALUES (%s, %s, %s)",
                (course_code, sem_id, enrolled_date)
            )
        conn.commit()
        click.echo(f"{course_code}-{course_name} created in semester {sem_id}")
    except IntegrityError:
        click.echo(f"{course_code}-{course_name} in semester {sem_id} already exists.")
    except Exception as e:
        click.echo(f"Error creating offering: {e}")
    finally:
        conn.close()

@offer_cli.command("update")
@click.argument("course_code")
@click.argument("semester_id")
@click.option("--date", "new_date", default=None, help="New enrollment date")
@click.option("--name", "new_name", default=None, help="New course name.")
@click.option("--code", "new_code", default=None, help="New course code.")
def update_offer(course_code, semester_id, new_date, new_name, new_code):
    if not (new_date or new_name or new_code):
        return click.echo("Nothing to update. Use --date, --name and/or --code.")
    if new_date:
        sem_id, sem_start, sem_end = compute_semester_id(new_date)
        try:
            create_semester.callback(sem_id, sem_start, sem_end)
        except Exception:
            pass
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE offers SET semester_id=%s, enrolled_at=%s 
                WHERE course_code=%s AND semester_id=%s
            """, (sem_id, new_date, course_code, semester_id)
            )
            conn.commit()
        click.echo(f"Semester moved to {sem_id}")
        semester_id = sem_id
    if new_name:
        update_course.callback(course_code, None, new_name)
        click.echo(f"Course Name set to “{new_name}”")
    if new_code:
        update_course.callback(course_code, new_code, None)
        click.echo(f"Course Code changed from {course_code} to {new_code}")
        course_code = new_code

    click.echo(f"Offering updated: {course_code}@{semester_id}")

@offer_cli.command("get")
@click.argument("course_code")
@click.argument("semester_id")
def get_offer(course_code: str, semester_id: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT o.course_code, c.name AS course_name, o.semester_id,
                       DATE_FORMAT(o.enrolled_at, '%%Y-%%m-%%d') AS enrolled_at
                FROM offers o JOIN courses c ON o.course_code = c.code
                WHERE o.course_code=%s
                  AND o.semester_id=%s
            """, (course_code, semester_id))
            row = cur.fetchone()
            if row:
                click.echo(row)
            else:
                click.echo(f"No offering found for {course_code} in {semester_id}")
    finally:
        conn.close()

@offer_cli.command("delete")
@click.argument("course_code")
@click.argument("semester_id")
def delete_offer(course_code: str, semester_id: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM offers WHERE course_code=%s AND semester_id=%s",
                (course_code, semester_id))
        conn.commit()
        click.echo(f"Offering {course_code}-{semester_id} deleted.")
    finally:
        conn.close()
