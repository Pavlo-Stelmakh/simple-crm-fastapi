from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from database import get_db_connection


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/web/stats")
def stats_page(request: Request):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM clients")
    clients_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM deals")
    deals_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM tasks")
    tasks_count = cursor.fetchone()["count"]

    cursor.execute("SELECT SUM(amount) AS total FROM deals")
    total_deals_amount = cursor.fetchone()["total"] or 0

    cursor.execute("""
        SELECT SUM(amount) AS total
        FROM deals
        WHERE status = 'won'
    """)
    won_deals_amount = cursor.fetchone()["total"] or 0

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM tasks
        WHERE is_done = 0
    """)
    open_tasks_count = cursor.fetchone()["count"]

    cursor.close()
    connection.close()

    stats = {
        "clients_count": clients_count,
        "deals_count": deals_count,
        "tasks_count": tasks_count,
        "total_deals_amount": total_deals_amount,
        "won_deals_amount": won_deals_amount,
        "open_tasks_count": open_tasks_count,
    }

    return templates.TemplateResponse(
        request=request,
        name="stats.html",
        context={
            "stats": stats,
        },
    )