from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Literal

# Define the valid task statuses centrally
TaskStatus = Literal[
    "running", 
    "queued", 
    "stopped", 
    "killed",
    "failed"
]

class ChatMessage(BaseModel):
    role: str
    text_content: str
    timestamp: Optional[datetime] = None


class Task(BaseModel):
    id: str
    name: str
    status: TaskStatus
    pid: Optional[int] = None
    heartbeat: Optional[datetime] = None
    created_at: Optional[datetime] = None


# --- Agent Action Models ---

class AgentDecision(BaseModel):
    """The structured decision output from Gemini."""
    thought: str = Field(..., description="The reasoning behind the current action.")
    action: Literal["run_command", "final_response"] = Field(..., description="What to do next.")
    command: Optional[str] = Field(None, description="The shell command to execute if action is run_command.")
    answer: Optional[str] = Field(None, description="The message to send to the user if action is final_response.")
