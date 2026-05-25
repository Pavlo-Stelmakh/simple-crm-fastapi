from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database import get_db_connection, init_db
from models import Client, Deal, Task
from routes.clients import router as clients_router
from routes.deals import router as deals_router
from routes.tasks import router as tasks_router
from routes.stats import router as stats_router
from routes.web import router as web_router

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

templates = Jinja2Templates(directory="templates")

init_db()
app.include_router(clients_router)
app.include_router(deals_router)
app.include_router(tasks_router)
app.include_router(stats_router)
app.include_router(web_router)


@app.get("/")
def home():
    return {"message": "CRM works with clients and deals"}
