#! /usr/bin/env python
import click
from .courses import course_cli
from .offers import offer_cli
from .semesters import semester_cli
from .staff import staff_cli
from .students import student_cli
from optimark.db import init_db, clean_db

@click.group()
def cli():
    pass

cli.add_command(course_cli)
cli.add_command(offer_cli)
cli.add_command(semester_cli)
cli.add_command(student_cli)
cli.add_command(staff_cli)


@cli.command("init-db")
def init_database():
    init_db()
    click.echo("Database Initialized.")

@cli.command("reset-db")
def reset_database():
    clean_db()
    init_db()
    click.echo("Database Reseted.")

if __name__ == '__main__':
    cli()