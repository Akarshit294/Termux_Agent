import aiosqlite
from typing import List
from .models import ChatMessage
from .connection import TELEGRAM_DB_PATH
from utils.logger import get_logger

log = get_logger(__name__, process_name="database")

async def init_db():
    """Create a fresh table for storing user-agent chats."""
    async with aiosqlite.connect(TELEGRAM_DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS telegram_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                text_content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
        log.info(f"SQLite database initialized at {TELEGRAM_DB_PATH}.")

async def save_telegram_message(message: ChatMessage):
    """Save a ChatMessage object in the database."""
    async with aiosqlite.connect(TELEGRAM_DB_PATH) as db:
        await db.execute(
            "INSERT INTO telegram_history (role, text_content) VALUES (?, ?)",
            (message.role, message.text_content)
        )
        await db.commit()

async def get_telegram_history(limit: int = 10) -> List[ChatMessage]:
    """Fetch recent data from the database and return as ChatMessage objects."""
    query = "SELECT role, text_content, timestamp FROM telegram_history ORDER BY id DESC LIMIT ?"
    async with aiosqlite.connect(TELEGRAM_DB_PATH) as db:
        async with db.execute(query, (limit,)) as cursor:
            rows = await cursor.fetchall()
            
    # Return as list of ChatMessage models
    return [
        ChatMessage(
            role=row[0],
            text_content=row[1],
            timestamp=row[2]
        ) for row in reversed(rows)
    ]

async def clear_telegram_history():
    """Wipes the table and reclaims physical disk space."""
    async with aiosqlite.connect(TELEGRAM_DB_PATH) as db:
        await db.execute("DELETE FROM telegram_history")
        await db.commit()
        await db.execute("VACUUM")
        log.info("Telegram history manually cleared by user.")
