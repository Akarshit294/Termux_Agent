import aiosqlite
from datetime import datetime
from typing import List, Optional
from .models import Task
from .connection import TASK_MANAGER_DB_PATH

async def init_task_table():
    """Ensure the task_manager table exists."""
    async with aiosqlite.connect(TASK_MANAGER_DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS task_manager (
                task_id TEXT PRIMARY KEY,
                task_name TEXT NOT NULL,
                status TEXT NOT NULL,
                pid INTEGER,
                last_heartbeat DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def insert_task(task: Task):
    """Insert a new Task object into the database."""
    async with aiosqlite.connect(TASK_MANAGER_DB_PATH) as db:
        await db.execute(
            "INSERT INTO task_manager (task_id, task_name, status, pid) VALUES (?, ?, ?, ?)",
            (task.id, task.name, task.status, task.pid)
        )
        await db.commit()

async def update_task_status(task_id: str, status: str):
    """Update a specific task's status."""
    async with aiosqlite.connect(TASK_MANAGER_DB_PATH) as db:
        await db.execute("UPDATE task_manager SET status = ? WHERE task_id = ?", (status, task_id))
        await db.commit()

async def update_task_heartbeat(task_id: str):
    """Update the heartbeat timestamp for a specific task."""
    async with aiosqlite.connect(TASK_MANAGER_DB_PATH) as db:
        await db.execute(
            "UPDATE task_manager SET last_heartbeat = CURRENT_TIMESTAMP WHERE task_id = ?", 
            (task_id,)
        )
        await db.commit()

async def get_all_tasks(status_filter: Optional[str] = None) -> List[Task]:
    """Fetch all tasks, optionally filtered by status, and return as Task objects."""
    query = "SELECT task_id, task_name, status, pid, last_heartbeat FROM task_manager"
    params = ()
    if status_filter:
        query += " WHERE status = ?"
        params = (status_filter,)
        
    async with aiosqlite.connect(TASK_MANAGER_DB_PATH) as db:
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [
                Task(
                    id=r[0],
                    name=r[1],
                    status=r[2],
                    pid=r[3],
                    heartbeat=datetime.fromisoformat(r[4]) if r[4] else None
                ) for r in rows
            ]

async def delete_task(task_id: str):
    """Remove a task from the database."""
    async with aiosqlite.connect(TASK_MANAGER_DB_PATH) as db:
        await db.execute("DELETE FROM task_manager WHERE task_id = ?", (task_id,))
        await db.commit()
