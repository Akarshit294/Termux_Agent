from pydantic import BaseModel
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

class GeminiContentPart(BaseModel):
    text: str

class GeminiContent(BaseModel):
    role: str
    parts: List[GeminiContentPart]

class Task(BaseModel):
    id: str
    name: str
    status: TaskStatus
    pid: Optional[int] = None
    heartbeat: Optional[datetime] = None
    created_at: Optional[datetime] = None
