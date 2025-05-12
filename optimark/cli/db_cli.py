#! /usr/bin/env python
import click
from .staff import staff_cli
from .students import student_cli
from optimark.db import init_db

@click.group()
def cli():
    pass

cli.add_command(student_cli)
cli.add_command(staff_cli)

@cli.command("init-db")
def init_database():
    init_db()
    click.echo("Database initialized.")

if __name__ == '__main__':
    cli()