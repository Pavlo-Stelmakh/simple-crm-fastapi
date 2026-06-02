import os

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    connection = psycopg2.connect(
        database_url,
        cursor_factory=RealDictCursor
    )

    return connection


def create_clients_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            company TEXT,
            comment TEXT
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()


def create_deals_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            amount REAL,
            status TEXT,
            comment TEXT,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()


def create_tasks_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL,
            deal_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            is_done INTEGER DEFAULT 0,
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (deal_id) REFERENCES deals (id)
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()


def init_db():
    create_clients_table()
    create_deals_table()
    create_tasks_table()