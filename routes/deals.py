from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from database import get_db_connection

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/web/deals")
def deals_page(request: Request):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT deals.*, clients.name AS client_name
        FROM deals
        JOIN clients ON deals.client_id = clients.id
        ORDER BY deals.id DESC
        """
    )
    deals = cursor.fetchall()

    cursor.execute(
        """
        SELECT *
        FROM clients
        ORDER BY name
        """
    )
    clients = cursor.fetchall()

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="deals.html",
        context={
            "deals": deals,
            "clients": clients,
        },
    )


@router.post("/web/deals")
def create_deal(
    client_id: int = Form(...),
    title: str = Form(...),
    amount: float = Form(0),
    status: str = Form("new"),
    comment: str = Form(""),
):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO deals (client_id, title, amount, status, comment)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (client_id, title, amount, status, comment),
    )

    connection.commit()

    cursor.close()
    connection.close()

    return RedirectResponse(url="/web/deals", status_code=303)


@router.get("/web/deals/{deal_id}")
def deal_detail_page(request: Request, deal_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT deals.*, clients.name AS client_name
        FROM deals
        JOIN clients ON deals.client_id = clients.id
        WHERE deals.id = %s
        """,
        (deal_id,),
    )
    deal = cursor.fetchone()

    cursor.execute(
        """
        SELECT *
        FROM tasks
        WHERE deal_id = %s
        ORDER BY id DESC
        """,
        (deal_id,),
    )
    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="deal_detail.html",
        context={
            "deal": deal,
            "tasks": tasks,
        },
    )


@router.get("/web/deals/{deal_id}/edit")
def edit_deal_page(request: Request, deal_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM deals
        WHERE id = %s
        """,
        (deal_id,),
    )
    deal = cursor.fetchone()

    cursor.execute(
        """
        SELECT *
        FROM clients
        ORDER BY name
        """
    )
    clients = cursor.fetchall()

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="edit_deal.html",
        context={
            "deal": deal,
            "clients": clients,
        },
    )


@router.post("/web/deals/{deal_id}/edit")
def update_deal(
    deal_id: int,
    client_id: int = Form(...),
    title: str = Form(...),
    amount: float = Form(0),
    status: str = Form("new"),
    comment: str = Form(""),
):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE deals
        SET client_id = %s,
            title = %s,
            amount = %s,
            status = %s,
            comment = %s
        WHERE id = %s
        """,
        (client_id, title, amount, status, comment, deal_id),
    )

    connection.commit()

    cursor.close()
    connection.close()

    return RedirectResponse(url=f"/web/deals/{deal_id}", status_code=303)


@router.post("/web/deals/{deal_id}/delete")
def delete_deal(deal_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE deal_id = %s
        """,
        (deal_id,),
    )

    cursor.execute(
        """
        DELETE FROM deals
        WHERE id = %s
        """,
        (deal_id,),
    )

    connection.commit()

    cursor.close()
    connection.close()

    return RedirectResponse(url="/web/deals", status_code=303)