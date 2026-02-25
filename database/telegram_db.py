import aiosqlite
from logger import get_logger


log = get_logger(__name__, process_name="database")
DB_PATH = "telegram.db"


async def init_db():
    """
    Create a fresh table for storing user-agent chats.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Isolated table just for Telegram chat
        await db.execute("""
            CREATE TABLE IF NOT EXISTS telegram_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                text_content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
        log.info("SQLite database initialized.")


async def save_telegram_message(role: str, text: str):
    """
    Function to save a message in db.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO telegram_history (role, text_content) VALUES (?, ?)",
            (role, text)
        )
        await db.commit()


async def get_telegram_history(limit: int = 10) -> list:
    """
    Fetch data from the db.
    """
    query = "SELECT role, text_content FROM telegram_history ORDER BY id DESC LIMIT ?"
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(query, (limit,)) as cursor:
            rows = await cursor.fetchall()
            
    history = []
    for role, text in reversed(rows):
        history.append({"role": role, "parts": [{"text": text}]})
    return history


async def clear_telegram_history():
    """
    Wipes the table and reclaims the physical disk space.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM telegram_history")
        await db.commit()
        await db.execute("VACUUM") # Shrinks the SQLite file back down
        log.info("Telegram history manually cleared by user.")