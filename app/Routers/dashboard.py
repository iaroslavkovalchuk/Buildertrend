from fastapi import FastAPI, APIRouter, Depends
from fastapi.responses import FileResponse
from fastapi import HTTPException, status, File, UploadFile

import os
import json
from dotenv import load_dotenv

from app.Utils.database_handler import DatabaseHandler
from app.Utils.chatgpt import get_last_message
from app.Utils.regular_update import job
from app.Utils.regular_send import send
from app.Utils.Auth import get_current_user


from datetime import datetime, timedelta
import asyncio
from typing import List, Annotated
from datetime import datetime

load_dotenv()
router = APIRouter()
db = DatabaseHandler()


@router.get('/update-db')
async def update_db(email: Annotated[str, Depends(get_current_user)]):
    job()
    return True


@router.get('/table')
async def get_table(email: Annotated[str, Depends(get_current_user)]):
    return db.get_main_table()
    


@router.get('/qued')
async def make_qued(email: Annotated[str, Depends(get_current_user)], project_id: int):
    qued_time = datetime.utcnow()
    project = db.get_project(project_id)
    db.set_project_status(project_id, 2, qued_time)
    return {"success": "true"}


@router.get('/cancel-qued')
async def cancel_qued(email: Annotated[str, Depends(get_current_user)], project_id: int):
    project = db.get_project(project_id)
    db.set_project_status(project_id, 1, None)
    return {"success": "true"}

@router.get('/set-sent')
async def set_sent(email: Annotated[str, Depends(get_current_user)], project_id: int):
    project = db.get_project(project_id)
    sent_time = datetime.utcnow()
    db.set_project_sent(project_id, 3, sent_time)
    ret = send(project_id)
    if ret == True:
        return {"success": "true"}
    else:
        return {"success": "false"}

@router.get('/change-status')
async def change_status(email: Annotated[str, Depends(get_current_user)], customer_id: int, method: int):
    db.update_sending_method(customer_id, method)
    return {"success": "true"}


@router.get('/update-last-message')
async def remove_last_message(email: Annotated[str, Depends(get_current_user)], project_id: int, message: str):
    db.update_last_message(project_id, message)
    return {"success": "true"}


@router.get('/download-project-message')
async def download_project_message(email: Annotated[str, Depends(get_current_user)], project_id: int):
    data = db.get_message_history_by_project_id(project_id)
    
    # Write data to a JSON file
    with open('message.txt', 'w') as f:
        json.dump(data, f)
    
    # Ensure file was saved
    if not os.path.exists('message.txt'):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Return file as response
    return FileResponse('message.txt', media_type='application/text', filename='message.txt')

@router.get('/download-customer-message')
async def download_user_message(email: Annotated[str, Depends(get_current_user)], customer_id: int):
    data = db.get_message_history_by_customer_id(customer_id)
    
    # Write data to a JSON file
    with open('message.txt', 'w') as f:
        json.dump(data, f)
    
    # Ensure file was saved
    if not os.path.exists('message.txt'):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Return file as response
    return FileResponse('message.txt', media_type='application/text', filename='message.txt')

@router.get('/delete-customer')
async def delete_customer(email: Annotated[str, Depends(get_current_user)], customer_id: int):
    db.delete_customer(customer_id)
    return True

@router.get('/send')
async def send_message(email: Annotated[str, Depends(get_current_user)]):
    send()
    return True