from fastapi import FastAPI,BackgroundTasks, APIRouter, Depends, HTTPException, status, File, UploadFile, Request, Form, Response
from fastapi.responses import FileResponse
from typing import List
from twilio.twiml.messaging_response import MessagingResponse
from sqlalchemy.orm import Session
from database import AsyncSessionLocal
import uuid


from app.Utils.chatgpt import get_last_message
from app.Utils.regular_send import send
from app.Utils.Auth import get_current_user
from app.Utils.regular_update import job, update_notification, update_database
from app.Utils.regular_send import send_opt_in_phone
from app.Utils.sendgrid import send_opt_in_email
import app.Utils.database_handler as crud
from app.Model.Settings import SettingsModel
from app.Model.MainTable import MainTableModel
from app.Model.ScrapingStatusModel import ScrapingStatusModel
from app.Model.LastMessageModel import LastMessageModel
from pydantic import EmailStr

from copy import deepcopy
from typing import Annotated
from datetime import datetime
import os
import json


from dotenv import load_dotenv


load_dotenv()
router = APIRouter()

# Dependency to get the database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post('/add-customer')
async def add_customer(data: MainTableModel, email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    print("dashboard - data: ", data)
    await crud.insert_customer(db, data)
    # Process the raw JSON data here
    return {"received": data, "message": "Raw data processed successfully"}

@router.post('/update-customer')
async def update_customer(data: MainTableModel, email: Annotated[str, Depends(get_current_user)], customer_id: int, db: Session = Depends(get_db)):
    print("dashboard - data: ", data)
    print("dashboard - customer_id: ", customer_id)
    await crud.update_customer(db, customer_id, data)
    return {"success": "true"}


@router.get('/delete-customer')
async def delete_customer_route(email: Annotated[str, Depends(get_current_user)], customer_id: int, db: Session = Depends(get_db)):
    await crud.delete_customer(db, customer_id)
    return {"success": "true"}


@router.get('/customer-table')
async def get_customer_table(db: Session = Depends(get_db)):
    main_table_data = await crud.get_main_table(db)  # Replace with appropriate await crud operation
    
    # Convert the SQLAlchemy result rows to dictionaries
    main_table_data_dicts = [
        {
            "id": data.id,
            "last_message": data.last_message,
            "message_status": data.message_status,
            "qued_timestamp": data.qued_timestamp,
            "sent_timestamp": data.sent_timestamp,
            "sent_success": data.sent_success,
            "image_url": data.image_url,
            "phone_numbers": data.phone_numbers,
            "num_sent": data.num_sent
        }
        for data in main_table_data
    ]
    
    return main_table_data_dicts

@router.get('/qued')
async def make_qued(email: Annotated[str, Depends(get_current_user)], project_id: int, db: Session = Depends(get_db)):
    qued_time = datetime.utcnow()
    # print("qued_time", qued_time)
    await crud.update_project(db, project_id, message_status=2, qued_timestamp=qued_time)
    return {"success": "true"}

@router.get('/cancel-qued')
async def cancel_qued(email: Annotated[str, Depends(get_current_user)], project_id: int, db: Session = Depends(get_db)):
    await crud.update_project(db, project_id, message_status=1, qued_timestamp=None)
    return {"success": "true"}

@router.get('/set-sent')
async def set_sent(email: Annotated[str, Depends(get_current_user)], project_id: int, db: Session = Depends(get_db)):
    sent_time = datetime.utcnow()
    print("sent_time", sent_time)
    await crud.update_project(db, project_id, message_status=3)
    ret = await send(project_id, db)  # Replace with appropriate send operation
    if ret:
        return {"success": "true"}
    else:
        return {"success": "false"}

@router.get('/change-status')
async def change_status(email: Annotated[str, Depends(get_current_user)], customer_id: int, method: int, db: Session = Depends(get_db)):
    await crud.update_sending_method(db, customer_id, method=method)
    return {"success": "true"}

@router.post('/update-last-message')
async def update_last_message(email: Annotated[str, Depends(get_current_user)], last_message: LastMessageModel, db: Session = Depends(get_db)):
    print("message: ", last_message.message)
    await crud.update_project(db, last_message.project_id, last_message=last_message.message)
    return {"success": "true"}

@router.get('/download-customer-message')
async def download_customer_message(email: Annotated[str, Depends(get_current_user)], customer_id: int, db: Session = Depends(get_db)):
    message = await crud.get_message_history_by_customer_id(db, customer_id)
    
    # Write data to a text file
    file_path = 'customer_message.txt'
    with open(file_path, 'w') as f:
        f.write(message + '\n')
    
    # Ensure file was saved
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Return file as response
    return FileResponse(file_path, media_type='application/octet-stream', filename='customer_message.txt')

@router.get('/download-history-message')
async def download_history_message(email: Annotated[str, Depends(get_current_user)], history_id: int, db: Session = Depends(get_db)):
    message = await crud.get_message_history_by_history_id(db, history_id)
    print(message)
    
    # Write data to a text file
    file_path = 'message.txt'
    with open(file_path, 'w') as f:
        f.write(message + '\n')
    
    # Ensure file was saved
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Return file as response
    return FileResponse(file_path, media_type='application/octet-stream', filename='message.txt')

@router.get('/send')
async def send_message_route(customer_id: int, email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    await send(customer_id, db)
    return {"success": "true"}

@router.post('/set-variables')
async def set_variables_route(variables: SettingsModel, db: Session = Depends(get_db)):
    
    data = await crud.get_variables(db)
    print(data)
    print("dashboard - set_variables", variables)
    if data is None:
        await crud.create_variables(db, **variables.dict())
    else:
        update_data = {k: (getattr(data, k) if v == "" else v) for k, v in variables.dict().items()}
        await crud.update_variables(db, data.id, **update_data)
    return {"success": "true"}

@router.get('/timer')
async def get_timer(email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    data = await crud.get_variables(db)
    if data is None:
        return None
    else:
        print(data.timer)
        return data.timer
        
        
    return {"success": "true"}


@router.get('/set-opt-in-status-email')
async def set_opt_in_status_email(email: Annotated[str, Depends(get_current_user)], customer_id: int, opt_in_status_email: int, db: Session = Depends(get_db)):
    print("dashboard - customer_id: ", customer_id)
    customer = await crud.get_customer(db, customer_id)
    if opt_in_status_email == 1:
        await send_opt_in_email(customer_id, customer.email, db)
    await crud.update_opt_in_status_email(db, customer_id, opt_in_status_email)
    return True

@router.get('/set-opt-in-status-phone')
async def set_opt_in_status_phone(email: Annotated[str, Depends(get_current_user)], customer_id: int, opt_in_status_phone: int, db: Session = Depends(get_db)):
    print("dashboard - customer_id: ", customer_id)
    customer = await crud.get_customer(db, customer_id)
    if opt_in_status_phone == 1:
        await send_opt_in_phone(customer.phone, db)
    await crud.update_opt_in_status_phone(db, customer_id, opt_in_status_phone)
    return True

@router.get('/confirm-opt-in-status')
async def set_opt_in_status(customer_id: int, response: str, db: Session = Depends(get_db)):
    print("dashboard - confirm-opt-in-status - customer_id: ", customer_id)
    
    await crud.update_opt_in_status_email(db, customer_id, 2 if response == "accept" else 3)
    
    data = await crud.get_status(db)
    if data is not None:
        await crud.set_db_update_status(db, data.id, 1)
    
    if response == "accept":
        return "Sent Successfully! Congulatulations!"
    else:
        return "Sent Successfully!"
    

@router.get('/approved')
async def set_opt_in_status(email: str, response: str, db: Session = Depends(get_db)):
    print("dashboard - approved - customer_id: ", email)
    user = await crud.get_user_by_email(db, email)
    
    if response == "accept":
        await crud.update_user(db, user.id, approved=1)
        return "Sent Successfully! Congulatulations!"
    else:
        await crud.update_user(db, user.id, approved=0)
        return "Sent Successfully!"
    



@router.get('/variables')
async def get_variables(email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    
    data = await crud.get_variables(db)
    return data

@router.get('/check-database-update')
async def get_variables(email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    
    data = await crud.get_status(db)
    if data is None:
        return False
    
    db_update_status = data.db_update_status
    print("dashboard - data.db_update_status: ", data.db_update_status)
    
    if db_update_status:
        await crud.set_db_update_status(db, data.id, 0)
        return True
    else:
        return False
