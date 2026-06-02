from fastapi import APIRouter, Depends

from auth import require_api_login
from database import get_db_connection


router = APIRouter(
    dependencies=[Depends(require_api_login)]
)


@router.get("/stats")
def get_stats():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count FROM clients
    """)
    clients_count = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) AS count FROM deals
    """)
    deals_count = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) AS count FROM tasks
    """)
    tasks_count = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT SUM(amount) AS total FROM deals
    """)
    total_deals_amount = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT SUM(amount) AS total FROM deals
        WHERE status = 'won'
    """)
    won_deals_amount = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS count FROM tasks
        WHERE is_done = 0
    """)
    open_tasks_count = cursor.fetchone()["count"]

    cursor.close()
    connection.close()

    return {
        "clients_count": clients_count,
        "deals_count": deals_count,
        "tasks_count": tasks_count,
        "total_deals_amount": total_deals_amount or 0,
        "won_deals_amount": won_deals_amount or 0,
        "open_tasks_count": open_tasks_count,
    }