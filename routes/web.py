from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from auth import is_logged_in, require_login, check_credentials


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/login")
def login_page(request: Request):
    if is_logged_in(request):
        return RedirectResponse(
            url="/web",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": None
        }
    )


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if check_credentials(username, password):
        response = RedirectResponse(
            url="/web",
            status_code=303
        )

        response.set_cookie(
            key="crm_auth",
            value="yes",
            httponly=True
        )

        return response

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": "Invalid username or password"
        },
        status_code=400
    )


@router.get("/logout")
def logout():
    response = RedirectResponse(
        url="/login",
        status_code=303
    )

    response.delete_cookie("crm_auth")

    return response


@router.get("/web")
def web_home(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={}
    )