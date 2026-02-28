import os

# Standardize where the DB files live
DB_DIR = "database_files"
os.makedirs(DB_DIR, exist_ok=True)

def get_db_path(db_name: str) -> str:
    """Returns the absolute path to a database file within the DB_DIR."""
    return os.path.join(DB_DIR, f"{db_name}.db")

# Predefined paths
TELEGRAM_DB_PATH = get_db_path("telegram")
TASK_MANAGER_DB_PATH = get_db_path("agent_state")
