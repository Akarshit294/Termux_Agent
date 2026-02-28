from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from llm.llm_gateway import llm_queue, queue_pause_event 
from database.telegram_db import clear_telegram_history
from database.models import TaskStatus
from services.task_manager import TaskManager
from utils.helpers import reply_to_me
from utils.logger import get_logger
from typing import Optional


log = get_logger(__name__, process_name="supervisor")

admin_router = Router()

import inspect
from functools import wraps

# A simple decorator-like approach for logging commands
def log_command(handler):
    @wraps(handler)
    async def wrapper(message: types.Message, *args, **kwargs):
        command_text = message.text.split()[0] if message.text else "unknown"
        log.info(f"Command received: {command_text} from {message.chat.id}")
        
        # Filter kwargs to only include what the handler expects
        sig = inspect.signature(handler)
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        
        return await handler(message, *args, **filtered_kwargs)
    return wrapper


@admin_router.message(Command("start"))
@log_command
async def cmd_start(message: types.Message, task_manager: TaskManager):
    """Initializes the session and provides a system status briefing."""
    
    # Fetch current task count for the briefing
    active_tasks = await task_manager.list_all_tasks(status="running")
    task_count = len(active_tasks)
    
    welcome_text = (
        "🤖 **Termux Agent Online**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🛰️ **Status:** `OPERATIONAL`\n"
        f"⚡ **Active Tasks:** `{task_count}` running\n"
        "🧠 **Memory Mode:** `SQLITE_PERSISTENT`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Welcome back, Commander. System architecture is verified. "
        "I am ready for Linux orchestration or specialized chat.\n\n"
        "💡 *Type /commands for tools or just talk to me.*"
    )
    await message.answer(welcome_text, parse_mode="Markdown")


@admin_router.message(Command("commands"))
@log_command
async def cmd_help(message: types.Message):
    """Lists all available administrative and task management commands."""
    help_text = (
        "🤖 **Termux Agent: Command Registry**\n\n"
        "**Core Control:**\n"
        "▫️ `/commands` - Show this registry.\n"
        "▫️ `/clear` - Reset chat memory (Wipe SQLite history).\n\n"
        "**LLM Gateway:**\n"
        "▫️ `/queued` - Check how many tasks are waiting for LLM.\n"
        "▫️ `/pause` - Halt background LLM processing.\n"
        "▫️ `/resume` - Continue background LLM processing.\n\n"
        "**Process Management:**\n"
        "▫️ `/tasks [status]` - List processes (e.g., `/tasks running`, `/tasks all`).\n"
        "▫️ `/stop <id>` - Terminate a specific task by its 8-char ID.\n"
        "▫️ `/kill` - The nuclear option: Kill ALL running tasks.\n"
        "▫️ `/prune` - Clean up dead/failed tasks from the database.\n\n"
        "💡 *Direct messages (no slash) will be routed to the LLM assistant.*"
    )
    await message.answer(help_text, parse_mode="Markdown")


@admin_router.message(Command("clear"))
@log_command
async def handle_clear_command(message: types.Message):
    """The Memory Reset Switch"""
    await clear_telegram_history()
    
    try:
        await message.delete()
    except Exception:
        pass
        
    blank_slate = (
        f"🧹   MEMORY CLEARED   🧹\n"
        "✨ Fresh start. Clean slate. ✨"
    )
    
    await message.answer(blank_slate, parse_mode="Markdown")


@admin_router.message(Command("tasks"))
@log_command
async def cmd_tasks(message: types.Message, command: CommandObject, task_manager: TaskManager):
    """Lists background tasks, optionally filtered by status."""
    requested_status = command.args.strip().lower() if command.args else "running"
    
    # Optional status filter based on our Literal TaskStatus
    status_filter: Optional[TaskStatus] = None
    if requested_status != "all":
        # We assume the user might type a valid status
        status_filter = requested_status if requested_status in ["running", "queued", "stopped", "killed", "failed"] else "running"
    
    # tasks is now a list of Task models
    tasks = await task_manager.list_all_tasks(status=status_filter)
    
    if not tasks:
        await message.answer(f"🟢 No background tasks found with status: **{requested_status}**.", parse_mode="Markdown")
        return
        
    header_emoji = "⚡" if requested_status == "running" else "📋"
    display_status = requested_status.upper()
    
    response = f"{header_emoji} **Tasks ({display_status}):**\n\n"
    
    for t in tasks:
        response += f"▫️ **ID:** `{t.id}`\n"
        response += f"   **Name:** {t.name}\n"
        response += f"   **Status:** {t.status}\n"
        if t.pid:
            response += f"   **PID:** {t.pid}\n"
        if t.heartbeat:
            response += f"   **Heartbeat:** {t.heartbeat.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
    if len(response) > 4000:
        response = response[:4000] + "\n... (List truncated to fit Telegram limits)"
        
    await message.answer(response, parse_mode="Markdown")


@admin_router.message(Command("queued"))
@log_command
async def cmd_queued(message: types.Message):
    """Shows how many tasks are waiting for the LLM."""
    q_size = llm_queue.qsize()
    status = "⏸️ PAUSED" if not queue_pause_event.is_set() else "▶️ RUNNING"
    await message.answer(f"📦 **LLM Queue Status:** {status}\nItems waiting: **{q_size}**", parse_mode="Markdown")


@admin_router.message(Command("pause"))
@log_command
async def cmd_pause(message: types.Message):
    """Locks the LLM worker so it stops processing background tasks."""
    queue_pause_event.clear()
    await message.answer("⏸️ **Queue Paused.** The LLM worker will not process new background tasks. Telegram chat retains 100% priority.", parse_mode="Markdown")


@admin_router.message(Command("resume"))
@log_command
async def cmd_resume(message: types.Message):
    """Unlocks the LLM worker."""
    queue_pause_event.set()
    await message.answer("▶️ **Queue Resumed.** Background tasks are now processing.", parse_mode="Markdown")


@admin_router.message(Command("stop"))
@log_command
async def cmd_stop(message: types.Message, command: CommandObject, task_manager: TaskManager):
    """Kills a specific task by its 8-character ID."""
    if not command.args:
        await message.answer("⚠️ Please provide a task ID. Example: `/stop a1b2c3d4`", parse_mode="Markdown")
        return
        
    task_id = command.args.strip()
    result_msg = await task_manager.stop_process(task_id, force_kill=True)
    await message.answer(f"🛑 **Stop Command Executed:**\n`{result_msg}`", parse_mode="Markdown")


@admin_router.message(Command("kill"))
@log_command
async def cmd_kill_all(message: types.Message, task_manager: TaskManager):
    """The Nuclear Option: Sweeps and kills every running task in the database."""
    tasks = await task_manager.list_all_tasks(status="running")
    if not tasks:
        await message.answer("🟢 No running tasks to kill.")
        return
        
    await message.answer(f"☢️ **Executing mass kill on {len(tasks)} tasks...**")
    
    killed_count = 0
    for t in tasks:
        await task_manager.stop_process(t.id, force_kill=True)
        killed_count += 1
        
    await message.answer(f"💀 **Successfully killed {killed_count} background tasks.**", parse_mode="Markdown")


@admin_router.message(Command("prune"))
@log_command
async def cmd_prune(message: types.Message, task_manager: TaskManager):
    """Cleans up the database by deleting non-running tasks."""
    deleted = await task_manager.prune_dead_tasks() 
    await message.answer(f"🧹 **Database Pruned:** Removed {deleted} completed/failed tasks from history.", parse_mode="Markdown")


@admin_router.message(F.text.startswith("/"))
async def cmd_fallback(message: types.Message):
    """Catch-all for invalid commands."""
    cmd = message.text.split()[0]
    log.warning(f"Invalid command attempted: {cmd}")
    await message.answer(
        f"⚠️ `{cmd}` is not a valid command.\n\n"
        "Type `/commands` to see the full registry of available administrative tools.",
        parse_mode="Markdown"
    )
