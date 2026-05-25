from fastapi import APIRouter, HTTPException, Depends
from auth import require_api_login

from database import get_db_connection
from models import Client


router = APIRouter(
    dependencies=[Depends(require_api_login)]
)


@router.post("/clients")
def create_client(client: Client):
    connection = get_db_connection()

    cursor = connection.execute("""
        INSERT INTO clients (name, phone, email, company, comment)
        VALUES (?, ?, ?, ?, ?)
    """, (
        client.name,
        client.phone,
        client.email,
        client.company,
        client.comment
    ))

    connection.commit()

    new_client_id = cursor.lastrowid

    new_client = connection.execute("""
        SELECT * FROM clients WHERE id = ?
    """, (new_client_id,)).fetchone()

    connection.close()

    return dict(new_client)


@router.get("/clients")
def get_clients():
    connection = get_db_connection()

    clients = connection.execute("""
        SELECT * FROM clients
    """).fetchall()

    connection.close()

    return [dict(client) for client in clients]


@router.get("/clients/search")
def search_clients(query: str):
    connection = get_db_connection()

    search_text = f"%{query}%"

    clients = connection.execute("""
        SELECT * FROM clients
        WHERE name LIKE ?
           OR phone LIKE ?
           OR email LIKE ?
           OR company LIKE ?
           OR comment LIKE ?
    """, (
        search_text,
        search_text,
        search_text,
        search_text,
        search_text
    )).fetchall()

    connection.close()

    return [dict(client) for client in clients]


@router.get("/clients/{client_id}")
def get_client(client_id: int):
    connection = get_db_connection()

    client = connection.execute("""
        SELECT * FROM clients WHERE id = ?
    """, (client_id,)).fetchone()

    connection.close()

    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    return dict(client)


@router.put("/clients/{client_id}")
def update_client(client_id: int, updated_client: Client):
    connection = get_db_connection()

    existing_client = connection.execute("""
        SELECT * FROM clients WHERE id = ?
    """, (client_id,)).fetchone()

    if existing_client is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Client not found")

    connection.execute("""
        UPDATE clients
        SET name = ?, phone = ?, email = ?, company = ?, comment = ?
        WHERE id = ?
    """, (
        updated_client.name,
        updated_client.phone,
        updated_client.email,
        updated_client.company,
        updated_client.comment,
        client_id
    ))

    connection.commit()

    updated = connection.execute("""
        SELECT * FROM clients WHERE id = ?
    """, (client_id,)).fetchone()

    connection.close()

    return dict(updated)


@router.delete("/clients/{client_id}")
def delete_client(client_id: int):
    connection = get_db_connection()

    existing_client = connection.execute("""
        SELECT * FROM clients WHERE id = ?
    """, (client_id,)).fetchone()

    if existing_client is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Client not found")

    connection.execute("""
        DELETE FROM clients WHERE id = ?
    """, (client_id,))

    connection.commit()
    connection.close()

    return {
        "message": "Client deleted",
        "client": dict(existing_client)
    }


@router.get("/clients/{client_id}/deals")
def get_client_with_deals(client_id: int):
    connection = get_db_connection()

    client = connection.execute("""
        SELECT * FROM clients WHERE id = ?
    """, (client_id,)).fetchone()

    if client is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Client not found")

    deals = connection.execute("""
        SELECT * FROM deals WHERE client_id = ?
    """, (client_id,)).fetchall()

    connection.close()

    return {
        "client": dict(client),
        "deals": [dict(deal) for deal in deals]
    }


@router.get("/clients/{client_id}/full")
def get_full_client_card(client_id: int):
    connection = get_db_connection()

    client = connection.execute("""
        SELECT * FROM clients WHERE id = ?
    """, (client_id,)).fetchone()

    if client is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Client not found")

    deals = connection.execute("""
        SELECT * FROM deals WHERE client_id = ?
    """, (client_id,)).fetchall()

    tasks = connection.execute("""
        SELECT * FROM tasks WHERE client_id = ?
    """, (client_id,)).fetchall()

    connection.close()

    return {
        "client": dict(client),
        "deals": [dict(deal) for deal in deals],
        "tasks": [dict(task) for task in tasks]
    }