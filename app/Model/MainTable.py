from pydantic import BaseModel
from typing import List, Optional
from fastapi import Form
from datetime import datetime

class MainTableModel(BaseModel):
    customer_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    project_id: Optional[int] = None  # If project_id can be missing, make this Optional too
    claim_number: Optional[str] = None
    project_name: Optional[str] = None
    last_message: Optional[str] = None
    message_status: Optional[int] = None
    qued_timestamp: Optional[datetime] = None
    sent_timestamp: Optional[datetime] = None
    sending_method: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    phone_sent_success: Optional[int] = None
    email_sent_success: Optional[int] = None

class ProjectMessageModel(BaseModel):
    history_id: Optional[int]
    message: Optional[str]
    sent_timestamp: Optional[datetime]
    project_id: Optional[int]