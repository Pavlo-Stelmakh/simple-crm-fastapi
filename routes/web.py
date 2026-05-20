from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from database import get_db_connection


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/web")
def web_home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={}
    )

@router.get("/web/clients")
def web_clients(request: Request, query: str = ""):
    connection = get_db_connection()

    if query:
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
    else:
        clients = connection.execute("""
            SELECT * FROM clients
        """).fetchall()

    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="clients.html",
        context={
            "clients": [dict(client) for client in clients],
            "query": query
        }
    )


@router.post("/web/clients/add")
def web_add_client(
    name: str = Form(...),
    phone: str = Form(""),
    email: str = Form(""),
    company: str = Form(""),
    comment: str = Form("")
):
    connection = get_db_connection()

    connection.execute("""
        INSERT INTO clients (name, phone, email, company, comment)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        phone,
        email,
        company,
        comment
    ))

    connection.commit()
    connection.close()

    return RedirectResponse(
        url="/web/clients",
        status_code=303
    )


@router.get("/web/clients/{client_id}/edit")
def web_edit_client_page(request: Request, client_id: int):
    connection = get_db_connection()

    client = connection.execute("""
        SELECT * FROM clients WHERE id = ?
    """, (client_id,)).fetchone()

    connection.close()

    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    return templates.TemplateResponse(
        request=request,
        name="edit_client.html",
        context={
            "client": dict(client)
        }
    )


@router.post("/web/clients/{client_id}/edit")
def web_update_client(
    client_id: int,
    name: str = Form(...),
    phone: str = Form(""),
    email: str = Form(""),
    company: str = Form(""),
    comment: str = Form("")
):
    connection = get_db_connection()

    connection.execute("""
        UPDATE clients
        SET name = ?, phone = ?, email = ?, company = ?, comment = ?
        WHERE id = ?
    """, (
        name,
        phone,
        email,
        company,
        comment,
        client_id
    ))

    connection.commit()
    connection.close()

    return RedirectResponse(
        url="/web/clients",
        status_code=303
    )

@router.post("/web/clients/{client_id}/delete")
def web_delete_client(client_id: int):
    connection = get_db_connection()

    deals_count = connection.execute("""
        SELECT COUNT(*) AS count FROM deals
        WHERE client_id = ?
    """, (client_id,)).fetchone()["count"]

    tasks_count = connection.execute("""
        SELECT COUNT(*) AS count FROM tasks
        WHERE client_id = ?
    """, (client_id,)).fetchone()["count"]

    if deals_count > 0 or tasks_count > 0:
        connection.close()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete client with existing deals or tasks"
        )

    connection.execute("""
        DELETE FROM clients WHERE id = ?
    """, (client_id,))

    connection.commit()
    connection.close()

    return RedirectResponse(
        url="/web/clients",
        status_code=303
    )

@router.get("/web/clients/{client_id}/full")
def web_full_client_card(request: Request, client_id: int):
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

    return templates.TemplateResponse(
        request=request,
        name="client_full.html",
        context={
            "client": dict(client),
            "deals": [dict(deal) for deal in deals],
            "tasks": [dict(task) for task in tasks]
        }
    )

@router.get("/web/deals")
def web_deals(request: Request, status: str = ""):
    connection = get_db_connection()

    clients = connection.execute("""
        SELECT * FROM clients
    """).fetchall()

    if status:
        deals = connection.execute("""
            SELECT 
                deals.id,
                deals.client_id,
                clients.name AS client_name,
                deals.title,
                deals.amount,
                deals.status,
                deals.comment
            FROM deals
            JOIN clients ON deals.client_id = clients.id
            WHERE deals.status = ?
        """, (status,)).fetchall()
    else:
        deals = connection.execute("""
            SELECT 
                deals.id,
                deals.client_id,
                clients.name AS client_name,
                deals.title,
                deals.amount,
                deals.status,
                deals.comment
            FROM deals
            JOIN clients ON deals.client_id = clients.id
        """).fetchall()

    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="deals.html",
        context={
            "clients": [dict(client) for client in clients],
            "deals": [dict(deal) for deal in deals],
            "status": status
        }
    )


@router.post("/web/deals/add")
def web_add_deal(
    client_id: int = Form(...),
    title: str = Form(...),
    amount: float = Form(0),
    status: str = Form("new"),
    comment: str = Form("")
):
    connection = get_db_connection()

    client = connection.execute("""
        SELECT * FROM clients WHERE id = ?
    """, (client_id,)).fetchone()

    if client is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Client not found")

    connection.execute("""
        INSERT INTO deals (client_id, title, amount, status, comment)
        VALUES (?, ?, ?, ?, ?)
    """, (
        client_id,
        title,
        amount,
        status,
        comment
    ))

    connection.commit()
    connection.close()

    return RedirectResponse(
        url="/web/deals",
        status_code=303
    )


@router.get("/web/deals/{deal_id}/edit")
def web_edit_deal_page(request: Request, deal_id: int):
    connection = get_db_connection()

    deal = connection.execute("""
        SELECT * FROM deals WHERE id = ?
    """, (deal_id,)).fetchone()

    clients = connection.execute("""
        SELECT * FROM clients
    """).fetchall()

    connection.close()

    if deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")

    return templates.TemplateResponse(
        request=request,
        name="edit_deal.html",
        context={
            "deal": dict(deal),
            "clients": [dict(client) for client in clients]
        }
    )


@router.post("/web/deals/{deal_id}/edit")
def web_update_deal(
    deal_id: int,
    client_id: int = Form(...),
    title: str = Form(...),
    amount: float = Form(0),
    status: str = Form("new"),
    comment: str = Form("")
):
    connection = get_db_connection()

    connection.execute("""
        UPDATE deals
        SET client_id = ?, title = ?, amount = ?, status = ?, comment = ?
        WHERE id = ?
    """, (
        client_id,
        title,
        amount,
        status,
        comment,
        deal_id
    ))

    connection.commit()
    connection.close()

    return RedirectResponse(
        url="/web/deals",
        status_code=303
    )


@router.post("/web/deals/{deal_id}/delete")
def web_delete_deal(deal_id: int):
    connection = get_db_connection()

    connection.execute("""
        DELETE FROM deals WHERE id = ?
    """, (deal_id,))

    connection.commit()
    connection.close()

    return RedirectResponse(
        url="/web/deals",
        status_code=303
    )

@router.get("/web/tasks")
def web_tasks(request: Request):
    connection = get_db_connection()

    clients = connection.execute("""
        SELECT * FROM clients
    """).fetchall()

    deals = connection.execute("""
        SELECT * FROM deals
    """).fetchall()

    tasks = connection.execute("""
        SELECT 
            tasks.id,
            tasks.client_id,
            clients.name AS client_name,
            tasks.deal_id,
            deals.title AS deal_title,
            tasks.title,
            tasks.description,
            tasks.due_date,
            tasks.is_done
        FROM tasks
        JOIN clients ON tasks.client_id = clients.id
        LEFT JOIN deals ON tasks.deal_id = deals.id
    """).fetchall()

    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="tasks.html",
        context={
            "clients": [dict(client) for client in clients],
            "deals": [dict(deal) for deal in deals],
            "tasks": [dict(task) for task in tasks]
        }
    )


@router.post("/web/tasks/add")
def web_add_task(
    client_id: int = Form(...),
    deal_id: str = Form(""),
    title: str = Form(...),
    description: str = Form(""),
    due_date: str = Form(""),
    is_done: str | None = Form(None)
):
    connection = get_db_connection()

    final_deal_id = None
    if deal_id != "":
        final_deal_id = int(deal_id)

    done_value = 1 if is_done == "1" else 0

    connection.execute("""
        INSERT INTO tasks (client_id, deal_id, title, description, due_date, is_done)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        client_id,
        final_deal_id,
        title,
        description,
        due_date,
        done_value
    ))

    connection.commit()
    connection.close()

    return RedirectResponse(
        url="/web/tasks",
        status_code=303
    )


@router.post("/web/tasks/{task_id}/done")
def web_mark_task_done(task_id: int):
    connection = get_db_connection()

    connection.execute("""
        UPDATE tasks
        SET is_done = 1
        WHERE id = ?
    """, (task_id,))

    connection.commit()
    connection.close()

    return RedirectResponse(
        url="/web/tasks",
        status_code=303
    )


@router.post("/web/tasks/{task_id}/delete")
def web_delete_task(task_id: int):
    connection = get_db_connection()

    connection.execute("""
        DELETE FROM tasks WHERE id = ?
    """, (task_id,))

    connection.commit()
    connection.close()

    return RedirectResponse(
        url="/web/tasks",
        status_code=303
    )


@router.get("/web/stats")
def web_stats(request: Request):
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

    stats = {
        "clients_count": clients_count,
        "deals_count": deals_count,
        "tasks_count": tasks_count,
        "total_deals_amount": total_deals_amount or 0,
        "won_deals_amount": won_deals_amount or 0,
        "open_tasks_count": open_tasks_count
    }

    return templates.TemplateResponse(
        request=request,
        name="stats.html",
        context={
            "stats": stats
        }
    )



