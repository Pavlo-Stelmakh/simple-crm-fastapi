from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from database import get_db_connection

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/web/clients")
def clients_page(request: Request, search: str = ""):
    connection = get_db_connection()
    cursor = connection.cursor()

    if search:
        cursor.execute(
            """
            SELECT *
            FROM clients
            WHERE name ILIKE %s
               OR phone ILIKE %s
               OR email ILIKE %s
               OR company ILIKE %s
            ORDER BY id DESC
            """,
            (
                f"%{search}%",
                f"%{search}%",
                f"%{search}%",
                f"%{search}%",
            ),
        )
    else:
        cursor.execute(
            """
            SELECT *
            FROM clients
            ORDER BY id DESC
            """
        )

    clients = cursor.fetchall()

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        "clients.html",
        {
            "request": request,
            "clients": clients,
            "search": search,
        },
    )


@router.post("/web/clients")
def create_client(
    name: str = Form(...),
    phone: str = Form(""),
    email: str = Form(""),
    company: str = Form(""),
    comment: str = Form(""),
):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO clients (name, phone, email, company, comment)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (name, phone, email, company, comment),
    )

    connection.commit()

    cursor.close()
    connection.close()

    return RedirectResponse(url="/web/clients", status_code=303)


@router.get("/web/clients/{client_id}")
def client_detail_page(request: Request, client_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM clients
        WHERE id = %s
        """,
        (client_id,),
    )
    client = cursor.fetchone()

    cursor.execute(
        """
        SELECT *
        FROM deals
        WHERE client_id = %s
        ORDER BY id DESC
        """,
        (client_id,),
    )
    deals = cursor.fetchall()

    cursor.execute(
        """
        SELECT *
        FROM tasks
        WHERE client_id = %s
        ORDER BY id DESC
        """,
        (client_id,),
    )
    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        "client_detail.html",
        {
            "request": request,
            "client": client,
            "deals": deals,
            "tasks": tasks,
        },
    )


@router.get("/web/clients/{client_id}/edit")
def edit_client_page(request: Request, client_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM clients
        WHERE id = %s
        """,
        (client_id,),
    )
    client = cursor.fetchone()

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        "edit_client.html",
        {
            "request": request,
            "client": client,
        },
    )


@router.post("/web/clients/{client_id}/edit")
def update_client(
    client_id: int,
    name: str = Form(...),
    phone: str = Form(""),
    email: str = Form(""),
    company: str = Form(""),
    comment: str = Form(""),
):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE clients
        SET name = %s,
            phone = %s,
            email = %s,
            company = %s,
            comment = %s
        WHERE id = %s
        """,
        (name, phone, email, company, comment, client_id),
    )

    connection.commit()

    cursor.close()
    connection.close()

    return RedirectResponse(url=f"/web/clients/{client_id}", status_code=303)


@router.post("/web/clients/{client_id}/delete")
def delete_client(client_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE client_id = %s
        """,
        (client_id,),
    )

    cursor.execute(
        """
        DELETE FROM deals
        WHERE client_id = %s
        """,
        (client_id,),
    )

    cursor.execute(
        """
        DELETE FROM clients
        WHERE id = %s
        """,
        (client_id,),
    )

    connection.commit()

    cursor.close()
    connection.close()

    return RedirectResponse(url="/web/clients", status_code=303)