import logging
import sys
import io
from logging.handlers import RotatingFileHandler
import os


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Ensure stdout/stderr handle UTF-8 correctly on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_HANDLERS = {}


def get_logger(module_name: str, process_name: str = "system"):
    """
    Returns a logger. Modules sharing the same process_name will 
    safely share the same file handler to prevent OS lock conflicts.
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)
    
    logger.propagate = False

    if not logger.handlers:
        if process_name not in _HANDLERS:
            file_path = os.path.join(LOG_DIR, f"{process_name}.log")
            
            # Use encoding="utf-8" for the file handler
            file_handler = RotatingFileHandler(
                file_path,
                maxBytes=5 * 1024 * 1024, 
                backupCount=2,
                encoding="utf-8"
            )

            console_handler = logging.StreamHandler(sys.stdout)

            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            _HANDLERS[process_name] = [file_handler, console_handler]

        for handler in _HANDLERS[process_name]:
            logger.addHandler(handler)

    return logger