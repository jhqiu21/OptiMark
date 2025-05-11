#! /usr/bin/env python

import uuid
import pymysql
import click
from dotenv import load_dotenv
import os
import hashlib
import string
import random
import secrets
from datetime import datetime


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '../db/schema.sql')

DB_HOST = os.getenv('OPTIMARK_DB_HOST')
DB_PORT = int(os.getenv('OPTIMARK_DB_PORT'))
DB_USER = os.getenv('OPTIMARK_DB_USER')
DB_PASS = os.getenv('OPTIMARK_DB_PASS')
DB_NAME = os.getenv('OPTIMARK_DB_NAME')

def get_connection():
    return pymysql.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASS,
        db=DB_NAME, charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def init_db():
    conn = get_connection()
    with conn.cursor() as cur, open(SCHEMA_PATH, 'r') as f:
        sql = f.read()
        for stmt in sql.split(';'):
            stmt = stmt.strip()
            if not stmt:
                continue
            cur.execute(stmt)
    conn.commit()
    conn.close()


@click.group()
def cli():
    """OptiMark tasks table CLI."""
    pass

@cli.command()
@click.argument('user_id')
@click.argument('task_name')
def create(user_id, task_name):
    """Create a new task for given USER_ID."""
    task_id = uuid.uuid4().hex[:8]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = "INSERT INTO tasks (id, user_id, name) VALUES (%s, %s, %s)"
            cur.execute(sql, (task_id, user_id, task_name))
        conn.commit()
        click.echo(f"Created task {task_id} - {task_name} for user {user_id}")
    finally:
        conn.close()

@cli.command()
@click.argument('task_id')
def get(task_id):
    """Get task record by TASK_ID."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id=%s", (task_id,))
            row = cur.fetchone()
            if row:
                click.echo(row)
            else:
                click.echo(f"No task found with id {task_id}")
    finally:
        conn.close()

@cli.command()
@click.argument('task_id')
@click.argument('status')
def update(task_id, status):
    """Update STATUS of existing task TASK_ID."""
    if status not in ('pending', 'processing', 'done', 'failed'):
        click.echo("Status must be one of: pending, processing, done, failed")
        return
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET status=%s WHERE id=%s",
                (status, task_id)
            )
        conn.commit()
        click.echo(f"Updated task {task_id} to status {status}")
    finally:
        conn.close()

@cli.command()
@click.argument('task_id')
def delete(task_id):
    """Delete task by TASK_ID."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
        conn.commit()
        click.echo(f"Deleted task {task_id}")
    finally:
        conn.close()

@cli.command('list')
def list_tasks():
    """List all tasks in the database."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, user_id, status, 
                       DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') AS created_at,
                       DATE_FORMAT(updated_at, '%Y-%m-%d %H:%i:%s') AS updated_at
                FROM tasks
                ORDER BY created_at DESC
            """)
            rows = cur.fetchall()
            if not rows:
                click.echo("No tasks found.")
                return
            # print header
            click.echo(f"{'ID':8} {'NAME':18} {'USER_ID':8}  {'STATUS':10}  {'CREATED_AT':19}  {'UPDATED_AT':19}")
            click.echo("-" * 120)
            # print each row of table
            for r in rows:
                click.echo(f"{r['id']:8} {r['name']:18} {r['user_id']:8}  {r['status']:10}  {r['created_at']:19}  {r['updated_at']:19}")
    finally:
        conn.close()

def hash_password(raw: str) -> str:
    """SHA-256 for raw password"""
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def generate_user_id(username: str, user_type: str) -> str:
    """Generates 8 bits user_id using username and user_type"""
    STUDENT_PREFIXES = ['A','B','E','H']
    TEACHER_PREFIXES = ['S','P','M']
    salt = secrets.token_hex(2)
    name_bytes = f"{username}{salt}".encode('utf-8')
    
    if user_type == 'student':
        prefix = STUDENT_PREFIXES[hashlib.sha1(name_bytes).digest()[0] % len(STUDENT_PREFIXES)]
    else: 
        prefix = TEACHER_PREFIXES[hashlib.sha1(name_bytes).digest()[0] % len(TEACHER_PREFIXES)]

    num = int(hashlib.md5(name_bytes).hexdigest(), 16) % 1_000_000
    middle = f"{num:06d}"

    idx = int(hashlib.sha256(name_bytes).hexdigest(), 16) % 26
    last = string.ascii_uppercase[idx]
    
    if last == prefix:
        last = string.ascii_uppercase[(idx + 1) % 26]

    return f"{prefix}{middle}{last}"

@cli.command('create-user')
@click.argument('user_name')
@click.argument('user_type')
@click.argument('password')
def create_user(user_name, user_type, password):
    user_id = generate_user_id(user_name, user_type)
    pwd_hash = hash_password(password)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (id, name, user_type, password)
                VALUES (%s, %s, %s, %s)
            """, (user_id, user_name, user_type, pwd_hash))
        conn.commit()
        click.echo(f"{user_name} - {user_id}({user_type}) is created successfully!")
    except pymysql.err.IntegrityError:
        click.echo(f"Error: User {user_id} exists!")
    finally:
        conn.close()

@cli.command('get-user')
@click.argument('user_id')
def get_user(user_id):
    """Get user information by user id"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            user = cur.fetchone()
            if not user:
                click.echo(f"No user found with id {user_id}")
            else:
                click.echo(user)
    finally:
        conn.close()

@cli.command('update-user')
@click.argument('user_id')
@click.option('--password', help="New Password")
@click.option('--user_type', type=click.Choice(['student','teacher']), help="Update User Type")
def update_user(user_id, password, user_type):
    if not password and not user_type:
        click.echo("Error: Please specify --password or --user_type")
        return
    
    fields, params = [], []
    if password:
        fields.append("password=%s")
        params.append(hash_password(password))
    if user_type:
        fields.append("user_type=%s")
        params.append(user_type)
    params.append(user_id)

    sql = f"UPDATE users SET {', '.join(fields)}, updated_at=NOW() WHERE id=%s"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
        conn.commit()
        click.echo(f"User {user_id} is updated successfully")
    finally:
        conn.close()


@cli.command('list-users')
def list_users():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, user_type,
                       DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') AS created_at
                FROM users
                ORDER BY created_at DESC
            """)
            rows = cur.fetchall()
            if not rows:
                click.echo("No users found.")
                return
            click.echo(f"{'ID':8} {'NAME'} {'TYPE':7}  {'CREATED_AT'}")
            click.echo("-"*40)
            for u in rows:
                click.echo(f"{u['id']:8} {u['name']} {u['user_type']:7}  {u['created_at']}")
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    cli()