from fastapi import APIRouter, HTTPException

from database import get_db_connection
from models import Task


router = APIRouter()


@router.post("/tasks")
def create_task(task: Task):
    connection = get_db_connection()

    client = connection.execute("""
        SELECT * FROM clients WHERE id = ?
    """, (task.client_id,)).fetchone()

    if client is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Client not found")

    if task.deal_id is not None:
        deal = connection.execute("""
            SELECT * FROM deals WHERE id = ?
        """, (task.deal_id,)).fetchone()

        if deal is None:
            connection.close()
            raise HTTPException(status_code=404, detail="Deal not found")

    cursor = connection.execute("""
        INSERT INTO tasks (client_id, deal_id, title, description, due_date, is_done)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        task.client_id,
        task.deal_id,
        task.title,
        task.description,
        task.due_date,
        int(task.is_done)
    ))

    connection.commit()

    new_task_id = cursor.lastrowid

    new_task = connection.execute("""
        SELECT * FROM tasks WHERE id = ?
    """, (new_task_id,)).fetchone()

    connection.close()

    return dict(new_task)


@router.get("/tasks")
def get_tasks():
    connection = get_db_connection()

    tasks = connection.execute("""
        SELECT * FROM tasks
    """).fetchall()

    connection.close()

    return [dict(task) for task in tasks]


@router.get("/tasks/{task_id}")
def get_task(task_id: int):
    connection = get_db_connection()

    task = connection.execute("""
        SELECT * FROM tasks WHERE id = ?
    """, (task_id,)).fetchone()

    connection.close()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return dict(task)


@router.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Task):
    connection = get_db_connection()

    existing_task = connection.execute("""
        SELECT * FROM tasks WHERE id = ?
    """, (task_id,)).fetchone()

    if existing_task is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Task not found")

    client = connection.execute("""
        SELECT * FROM clients WHERE id = ?
    """, (updated_task.client_id,)).fetchone()

    if client is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Client not found")

    if updated_task.deal_id is not None:
        deal = connection.execute("""
            SELECT * FROM deals WHERE id = ?
        """, (updated_task.deal_id,)).fetchone()

        if deal is None:
            connection.close()
            raise HTTPException(status_code=404, detail="Deal not found")

    connection.execute("""
        UPDATE tasks
        SET client_id = ?, deal_id = ?, title = ?, description = ?, due_date = ?, is_done = ?
        WHERE id = ?
    """, (
        updated_task.client_id,
        updated_task.deal_id,
        updated_task.title,
        updated_task.description,
        updated_task.due_date,
        int(updated_task.is_done),
        task_id
    ))

    connection.commit()

    updated = connection.execute("""
        SELECT * FROM tasks WHERE id = ?
    """, (task_id,)).fetchone()

    connection.close()

    return dict(updated)


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    connection = get_db_connection()

    existing_task = connection.execute("""
        SELECT * FROM tasks WHERE id = ?
    """, (task_id,)).fetchone()

    if existing_task is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Task not found")

    connection.execute("""
        DELETE FROM tasks WHERE id = ?
    """, (task_id,))

    connection.commit()
    connection.close()

    return {
        "message": "Task deleted",
        "task": dict(existing_task)
    }