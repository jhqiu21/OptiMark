#! /usr/bin/env python

import pymysql
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
base = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
SCHEMA_PATH = os.path.join(base, 'db', 'schema.sql')

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