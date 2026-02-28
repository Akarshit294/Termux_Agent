import os
from utils.logger import get_logger

log = get_logger(__name__)

PROMPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(PROMPTS_DIR)

def get_prompt(filename: str, pipeline: str = "default") -> str:
    """
    Finds and reads a prompt file. 
    If pipeline is 'telegram', it merges the README for context awareness.
    """
    # 1. Load the primary prompt
    primary_prompt = _read_file(os.path.join(PROMPTS_DIR, filename))
    
    # 2. Add pipeline-specific context
    if pipeline == "telegram":
        readme_path = os.path.join(ROOT_DIR, "README.md")
        readme_content = _read_file(readme_path)
        
        context_wrapper = (
            f"{primary_prompt}\n\n"
            f"--- PROJECT CONTEXT (README.md) ---\n"
            f"{readme_content}\n"
            f"--- END OF CONTEXT ---"
        )
        return context_wrapper

    return primary_prompt

def _read_file(path: str) -> str:
    """Helper to safely read a file with fallbacks."""
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception as e:
        log.error(f"Failed to read file at {path}: {e}")
    
    return ""
