from pydantic import BaseModel
from typing import List, Optional
from fastapi import Form
from datetime import datetime

class MainTableModel(BaseModel):
    customer_id: Optional[int]
    firstname: Optional[str]
    lastname: Optional[str]
    project_id: int
    claim_number: Optional[str]
    last_message: Optional[str]
    message_status: Optional[int]
    qued_timestamp: Optional[datetime]
    sent_timestamp: Optional[datetime]
    sending_method: Optional[int]
    email: Optional[str]
    phone: Optional[str]
    phone_sent_success: Optional[int]
    email_sent_success: Optional[int]

class ProjectMessageModel(BaseModel):
    history_id: Optional[int]
    message: Optional[str]
    sent_timestamp: Optional[datetime]
    project_id: Optional[int]