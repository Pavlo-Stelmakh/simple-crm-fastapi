from pydantic import BaseModel


class Client(BaseModel):
    name: str
    phone: str = ""
    email: str = ""
    company: str = ""
    comment: str = ""


class Deal(BaseModel):
    client_id: int
    title: str
    amount: float = 0
    status: str = "new"
    comment: str = ""


class Task(BaseModel):
    client_id: int
    deal_id: int | None = None
    title: str
    description: str = ""
    due_date: str = ""
    is_done: bool = False