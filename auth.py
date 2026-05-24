from fastapi import Request
from fastapi.responses import RedirectResponse


def is_logged_in(request: Request) -> bool:
    return request.cookies.get("crm_auth") == "yes"


def require_login(request: Request):
    if not is_logged_in(request):
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return None