import sqlite3


def get_db_connection():
    connection = sqlite3.connect("crm.db")
    connection.row_factory = sqlite3.Row
    return connection


def create_clients_table():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            company TEXT,
            comment TEXT
        )
    """)

    connection.commit()
    connection.close()


def create_deals_table():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            amount REAL,
            status TEXT,
            comment TEXT,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    """)

    connection.commit()
    connection.close()


def create_tasks_table():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    connection.close()


def init_db():
    create_clients_table()
    create_deals_table()
    create_tasks_table()