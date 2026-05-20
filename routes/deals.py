from fastapi import APIRouter, HTTPException

from database import get_db_connection
from models import Deal


router = APIRouter()


@router.post("/deals")
def create_deal(deal: Deal):
    connection = get_db_connection()

    client = connection.execute("""
        SELECT * FROM clients WHERE id = ?
    """, (deal.client_id,)).fetchone()

    if client is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Client not found")

    cursor = connection.execute("""
        INSERT INTO deals (client_id, title, amount, status, comment)
        VALUES (?, ?, ?, ?, ?)
    """, (
        deal.client_id,
        deal.title,
        deal.amount,
        deal.status,
        deal.comment
    ))

    connection.commit()

    new_deal_id = cursor.lastrowid

    new_deal = connection.execute("""
        SELECT * FROM deals WHERE id = ?
    """, (new_deal_id,)).fetchone()

    connection.close()

    return dict(new_deal)


@router.get("/deals")
def get_deals():
    connection = get_db_connection()

    deals = connection.execute("""
        SELECT * FROM deals
    """).fetchall()

    connection.close()

    return [dict(deal) for deal in deals]


@router.get("/deals/status/{status}")
def get_deals_by_status(status: str):
    connection = get_db_connection()

    deals = connection.execute("""
        SELECT * FROM deals
        WHERE status = ?
    """, (status,)).fetchall()

    connection.close()

    return [dict(deal) for deal in deals]


@router.get("/deals/{deal_id}")
def get_deal(deal_id: int):
    connection = get_db_connection()

    deal = connection.execute("""
        SELECT * FROM deals WHERE id = ?
    """, (deal_id,)).fetchone()

    connection.close()

    if deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")

    return dict(deal)


@router.put("/deals/{deal_id}")
def update_deal(deal_id: int, updated_deal: Deal):
    connection = get_db_connection()

    existing_deal = connection.execute("""
        SELECT * FROM deals WHERE id = ?
    """, (deal_id,)).fetchone()

    if existing_deal is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Deal not found")

    client = connection.execute("""
        SELECT * FROM clients WHERE id = ?
    """, (updated_deal.client_id,)).fetchone()

    if client is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Client not found")

    connection.execute("""
        UPDATE deals
        SET client_id = ?, title = ?, amount = ?, status = ?, comment = ?
        WHERE id = ?
    """, (
        updated_deal.client_id,
        updated_deal.title,
        updated_deal.amount,
        updated_deal.status,
        updated_deal.comment,
        deal_id
    ))

    connection.commit()

    updated = connection.execute("""
        SELECT * FROM deals WHERE id = ?
    """, (deal_id,)).fetchone()

    connection.close()

    return dict(updated)


@router.delete("/deals/{deal_id}")
def delete_deal(deal_id: int):
    connection = get_db_connection()

    existing_deal = connection.execute("""
        SELECT * FROM deals WHERE id = ?
    """, (deal_id,)).fetchone()

    if existing_deal is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Deal not found")

    connection.execute("""
        DELETE FROM deals WHERE id = ?
    """, (deal_id,))

    connection.commit()
    connection.close()

    return {
        "message": "Deal deleted",
        "deal": dict(existing_deal)
    }