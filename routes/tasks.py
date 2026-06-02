from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from database import get_db_connection

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/web/tasks")
def tasks_page(request: Request):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            tasks.*,
            clients.name AS client_name,
            deals.title AS deal_title
        FROM tasks
        JOIN clients ON tasks.client_id = clients.id
        LEFT JOIN deals ON tasks.deal_id = deals.id
        ORDER BY tasks.id DESC
        """
    )
    tasks = cursor.fetchall()

    cursor.execute(
        """
        SELECT *
        FROM clients
        ORDER BY name
        """
    )
    clients = cursor.fetchall()

    cursor.execute(
        """
        SELECT *
        FROM deals
        ORDER BY title
        """
    )
    deals = cursor.fetchall()

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        "tasks.html",
        {
            "request": request,
            "tasks": tasks,
            "clients": clients,
            "deals": deals,
        },
    )


@router.post("/web/tasks")
def create_task(
    client_id: int = Form(...),
    deal_id: str = Form(""),
    title: str = Form(...),
    description: str = Form(""),
    due_date: str = Form(""),
):
    connection = get_db_connection()
    cursor = connection.cursor()

    deal_id_value = int(deal_id) if deal_id else None

    cursor.execute(
        """
        INSERT INTO tasks (client_id, deal_id, title, description, due_date, is_done)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (client_id, deal_id_value, title, description, due_date, 0),
    )

    connection.commit()

    cursor.close()
    connection.close()

    return RedirectResponse(url="/web/tasks", status_code=303)


@router.get("/web/tasks/{task_id}/edit")
def edit_task_page(request: Request, task_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tasks
        WHERE id = %s
        """,
        (task_id,),
    )
    task = cursor.fetchone()

    cursor.execute(
        """
        SELECT *
        FROM clients
        ORDER BY name
        """
    )
    clients = cursor.fetchall()

    cursor.execute(
        """
        SELECT *
        FROM deals
        ORDER BY title
        """
    )
    deals = cursor.fetchall()

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        "edit_task.html",
        {
            "request": request,
            "task": task,
            "clients": clients,
            "deals": deals,
        },
    )


@router.post("/web/tasks/{task_id}/edit")
def update_task(
    task_id: int,
    client_id: int = Form(...),
    deal_id: str = Form(""),
    title: str = Form(...),
    description: str = Form(""),
    due_date: str = Form(""),
    is_done: str = Form("0"),
):
    connection = get_db_connection()
    cursor = connection.cursor()

    deal_id_value = int(deal_id) if deal_id else None
    is_done_value = 1 if is_done == "1" else 0

    cursor.execute(
        """
        UPDATE tasks
        SET client_id = %s,
            deal_id = %s,
            title = %s,
            description = %s,
            due_date = %s,
            is_done = %s
        WHERE id = %s
        """,
        (
            client_id,
            deal_id_value,
            title,
            description,
            due_date,
            is_done_value,
            task_id,
        ),
    )

    connection.commit()

    cursor.close()
    connection.close()

    return RedirectResponse(url="/web/tasks", status_code=303)


@router.post("/web/tasks/{task_id}/done")
def mark_task_done(task_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET is_done = 1
        WHERE id = %s
        """,
        (task_id,),
    )

    connection.commit()

    cursor.close()
    connection.close()

    return RedirectResponse(url="/web/tasks", status_code=303)


@router.post("/web/tasks/{task_id}/delete")
def delete_task(task_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE id = %s
        """,
        (task_id,),
    )

    connection.commit()

    cursor.close()
    connection.close()

    return RedirectResponse(url="/web/tasks", status_code=303)