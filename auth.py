import os

from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import RedirectResponse


load_dotenv()

CRM_USERNAME = os.getenv("CRM_USERNAME", "admin")
CRM_PASSWORD = os.getenv("CRM_PASSWORD", "admin123")


def is_logged_in(request: Request) -> bool:
    return request.cookies.get("crm_auth") == "yes"


def check_credentials(username: str, password: str) -> bool:
    return username == CRM_USERNAME and password == CRM_PASSWORD


def require_login(request: Request):
    if not is_logged_in(request):
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return None