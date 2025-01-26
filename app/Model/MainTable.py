from pydantic import BaseModel
from typing import List, Optional
from fastapi import Form
from datetime import datetime

class MainTableModel(BaseModel):
    last_message: Optional[str] = None
    message_status: Optional[int] = None
    qued_timestamp: Optional[datetime] = None
    sent_timestamp: Optional[datetime] = None
    sent_success: Optional[int] = None
    image_url: Optional[str] = None
    phone_numbers: Optional[List[str]] = None
    num_sent: Optional[int] = None
    created_at: Optional[datetime] = None
    
class MessageModel(BaseModel):
    message: Optional[str]
    sent_timestamp: Optional[datetime]
    phone_number: Optional[str]
    opt_in_status: Optional[int]
    categories: Optional[List[str]]
    
    
    
    