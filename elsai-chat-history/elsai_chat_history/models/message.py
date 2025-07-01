import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Core message model for chat history."""
    
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the message was created")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    session_id: Optional[str] = Field(None, description="Session identifier")
    message_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message identifier")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)
