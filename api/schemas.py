from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProductCount(BaseModel):
    term: str
    count: int

class ChannelActivity(BaseModel):
    date: str
    message_count: int

class MessageResponse(BaseModel):
    message_id: int
    channel_name: str
    text: Optional[str]
    view_count: Optional[int]
    message_date: datetime

class VisualContentStats(BaseModel):
    channel_name: str
    image_category: str
    count: int