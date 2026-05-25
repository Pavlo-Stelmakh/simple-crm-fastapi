from fastapi import APIRouter, Depends
from auth import require_api_login

from database import get_db_connection


router = APIRouter(
    dependencies=[Depends(require_api_login)]
)


@router.get("/stats")
def get_stats():
    connection = get_db_connection()

    clients_count = connection.execute("""
        SELECT COUNT(*) AS count FROM clients
    """).fetchone()["count"]

    deals_count = connection.execute("""
        SELECT COUNT(*) AS count FROM deals
    """).fetchone()["count"]

    tasks_count = connection.execute("""
        SELECT COUNT(*) AS count FROM tasks
    """).fetchone()["count"]

    total_deals_amount = connection.execute("""
        SELECT SUM(amount) AS total FROM deals
    """).fetchone()["total"]

    won_deals_amount = connection.execute("""
        SELECT SUM(amount) AS total FROM deals
        WHERE status = 'won'
    """).fetchone()["total"]

    open_tasks_count = connection.execute("""
        SELECT COUNT(*) AS count FROM tasks
        WHERE is_done = 0
    """).fetchone()["count"]

    connection.close()

    return {
        "clients_count": clients_count,
        "deals_count": deals_count,
        "tasks_count": tasks_count,
        "total_deals_amount": total_deals_amount or 0,
        "won_deals_amount": won_deals_amount or 0,
        "open_tasks_count": open_tasks_count
    }