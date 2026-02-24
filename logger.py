import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Cache to share file handlers across different modules in the same process
_HANDLERS = {}

def get_logger(module_name: str, process_name: str = "system"):
    """
    Returns a logger. Modules sharing the same process_name will 
    safely share the same file handler to prevent OS lock conflicts.
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)
    
    # Prevent logs from bubbling up to the root logger and printing twice
    logger.propagate = False

    if not logger.handlers:
        # If we haven't created handlers for this process yet, build them
        if process_name not in _HANDLERS:
            file_path = os.path.join(LOG_DIR, f"{process_name}.log")
            
            # Set to 2048 (2KB) for testing, change back to 5*1024*1024 for prod
            file_handler = RotatingFileHandler(
                file_path,
                maxBytes=2048, 
                backupCount=3
            )
            console_handler = logging.StreamHandler()

            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Save these handlers in the cache
            _HANDLERS[process_name] = [file_handler, console_handler]

        # Attach the cached handlers to this specific module's logger
        for handler in _HANDLERS[process_name]:
            logger.addHandler(handler)

    return logger