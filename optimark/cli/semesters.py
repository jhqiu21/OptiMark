# optimark/cli/semesters.py
import click
from pymysql.err import IntegrityError
from optimark.db import get_connection

@click.group("semester")
def semester_cli():
    pass

@semester_cli.command("create")
@click.argument("id")
@click.argument("start_date")
@click.argument("end_date")
def create_semester(id: str, start_date: str, end_date: str):
    """
    Create a new semester.
    ID          : 6-char semester code, e.g. 2425S1  
    START_DATE  : in YYYY-MM-DD format  
    END_DATE    : in YYYY-MM-DD format  
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO semesters (id, start_date, end_date) VALUES (%s, %s, %s)",
                (id, start_date, end_date))
        conn.commit()
        click.echo(f"Semester {id} created: from {start_date} to {end_date}")
    except IntegrityError:
        click.echo(f"Semester {id} already exists.")
    except Exception as e:
        click.echo(f"Error creating semester: {e}")
    finally:
        conn.close()

