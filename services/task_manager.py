import os
import signal
import uuid
from utils.logger import get_logger
from database import task_manager_db
from database.models import Task, TaskStatus


log = get_logger(__name__)


class TaskManager:
    def __init__(self):
        # Private constructor. Use TaskManager.create() instead.
        pass


    @classmethod
    async def create(cls):
        """Factory method to ensure async DB initialization before returning the object."""
        await task_manager_db.init_task_table()
        instance = cls()
        await instance.rehydrate_tasks()
        return instance


    async def register_task(self, name: str, pid: int = None) -> str:
        """Creates a unique UUID for the task and logs it in SQLite."""
        task_id = str(uuid.uuid4())[:8]  # Short 8-char ID for easy Telegram typing
        
        # Initial status is 'running'
        task = Task(id=task_id, name=name, status="running", pid=pid)
        await task_manager_db.insert_task(task)

        log.info(f"Task registered: {name} (ID: {task_id}, PID: {pid})")
        return task_id


    async def remove_task(self, task_id: str):
        """Deletes the task from the database entirely."""
        await task_manager_db.delete_task(task_id)

        log.info(f"Task removed: {task_id}")


    async def update_heartbeat(self, task_id: str):
        """Pings SQLite to prove the task hasn't been killed by Android."""
        await task_manager_db.update_task_heartbeat(task_id)


    async def list_all_tasks(self, status: Optional[TaskStatus] = None) -> list:
        return await task_manager_db.get_all_tasks(status_filter=status)


    async def rehydrate_tasks(self):
        """
        Runs on boot. If the supervisor just restarted, anything marked 'running'
        is actually dead (orphaned by a previous crash). Mark them as 'failed'.
        """
        active_tasks = await self.list_all_tasks(status="running")
        for task in active_tasks:
            await task_manager_db.update_task_status(task.id, "failed")

            log.warning(f"Rehydrated orphan task to failed: {task.id}")
            

    async def stop_process(self, task_id: str, force_kill: bool = False):
        """Interacts with the Linux OS to terminate the actual process."""
        tasks = await self.list_all_tasks()
        task = next((t for t in tasks if t.id == task_id), None)
        
        if not task or not task.pid:
            log.info("Task or PID not found.")
            return "Task or PID not found."
            
        pid = task.pid
        try:
            # SIGTERM (15) asks politely. SIGKILL (9) forces immediate shutdown.
            sig = signal.SIGKILL if force_kill else signal.SIGTERM
            os.kill(pid, sig)
            
            # Map signal to our clean Literal statuses
            new_status: TaskStatus = "killed" if force_kill else "stopped"
            await task_manager_db.update_task_status(task_id, new_status)
            result = f"Successfully sent signal to PID {pid}. Status: {new_status}."
            
        except ProcessLookupError:
            # If the process is gone, it's 'failed' because it died unexpectedly
            await task_manager_db.update_task_status(task_id, "failed")
            result =  f"PID {pid} no longer exists in Termux. Marked as failed."
        except Exception as e:
            result =  f"Error stopping PID {pid}: {str(e)}"
        
        log.info(result)
        return result

    
    async def prune_dead_tasks(self) -> int:
        """Deletes all tasks that are not 'running' or 'queued'."""
        import aiosqlite
        from database.connection import TASK_MANAGER_DB_PATH
        async with aiosqlite.connect(TASK_MANAGER_DB_PATH) as db:
            # Only keep active lifecycle statuses
            cursor = await db.execute("DELETE FROM task_manager WHERE status NOT IN ('running', 'queued')")
            deleted_count = cursor.rowcount
            await db.commit()
        
        log.info(f"Deleted {deleted_count} tasks.")
        return deleted_count
