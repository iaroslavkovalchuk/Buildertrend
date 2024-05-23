from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, File, UploadFile, Request, Form
from fastapi.responses import FileResponse
from twilio.twiml.messaging_response import MessagingResponse
from sqlalchemy.orm import Session
from database import SessionLocal

from app.Utils.chatgpt import get_last_message
from app.Utils.regular_send import send
from app.Utils.Auth import get_current_user
from app.Model.Settings import SettingsModel
from app.Model.MainTable import MainTableModel
from app.Utils.regular_update import job, update_notification, update_database
from app.Utils.regular_send import send_opt_in_phone
from app.Utils.sendgrid import send_opt_in_email
import app.Utils.database_handler as crud

from typing import Annotated
from datetime import datetime
import os
import json


from dotenv import load_dotenv


load_dotenv()
router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/update-db')
def update_db(source: str, email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    print("dashboard - source: ", source)
    job(source)
    return True

@router.post('/get-scraped-result')
async def scraped_result(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    print("dashboard - data: ", data)
    update_database(data)
    # Process the raw JSON data here
    return {"received": len(data), "message": "Raw data processed successfully"}

@router.get('/table')
async def get_table(email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    main_table_data = crud.get_main_table(db)  # Replace with appropriate CRUD operation
    result = [MainTableModel(**item._asdict()) for item in main_table_data]

    return result

@router.get('/qued')
async def make_qued(email: Annotated[str, Depends(get_current_user)], project_id: int, db: Session = Depends(get_db)):
    qued_time = datetime.utcnow()
    # print("qued_time", qued_time)
    crud.update_project(db, project_id, message_status=2, qued_timestamp=qued_time)
    return {"success": "true"}

@router.get('/cancel-qued')
async def cancel_qued(email: Annotated[str, Depends(get_current_user)], project_id: int, db: Session = Depends(get_db)):
    crud.update_project(db, project_id, message_status=1, qued_timestamp=None)
    return {"success": "true"}

@router.get('/set-sent')
async def set_sent(email: Annotated[str, Depends(get_current_user)], project_id: int, db: Session = Depends(get_db)):
    sent_time = datetime.utcnow()
    print("sent_time", sent_time)
    crud.update_project(db, project_id, message_status=3, sent_timestamp=sent_time)
    ret = send(project_id, db)  # Replace with appropriate send operation
    if ret:
        return {"success": "true"}
    else:
        return {"success": "false"}

@router.get('/change-status')
async def change_status(email: Annotated[str, Depends(get_current_user)], customer_id: int, method: int, db: Session = Depends(get_db)):
    crud.update_sending_method(db, customer_id, method=method)
    return {"success": "true"}

@router.get('/update-last-message')
async def update_last_message(email: Annotated[str, Depends(get_current_user)], project_id: int, message: str, db: Session = Depends(get_db)):
    crud.update_project(db, project_id, last_message=message)
    return {"success": "true"}

@router.get('/download-project-message')
async def download_project_message(email: Annotated[str, Depends(get_current_user)], project_id: int, db: Session = Depends(get_db)):
    message = crud.get_message_history_by_project_id(db, project_id)
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



@router.get('/download-customer-message')
async def download_customer_message(email: Annotated[str, Depends(get_current_user)], customer_id: int, db: Session = Depends(get_db)):
    message = crud.get_message_history_by_customer_id(db, customer_id)
    
    # Write data to a text file
    file_path = 'customer_message.txt'
    with open(file_path, 'w') as f:
        f.write(message + '\n')
    
    # Ensure file was saved
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Return file as response
    return FileResponse(file_path, media_type='application/octet-stream', filename='customer_message.txt')

@router.get('/delete-customer')
async def delete_customer_route(email: Annotated[str, Depends(get_current_user)], customer_id: int, db: Session = Depends(get_db)):
    crud.delete_customer(db, customer_id)
    return {"success": "true"}

@router.get('/send')
async def send_message_route(email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    send()
    return {"success": "true"}

@router.post('/set-variables')
async def set_variables_route(variables: SettingsModel, db: Session = Depends(get_db)):
    
    data = crud.get_variables(db)
    print(data)
    print("dashboard - set_variables", variables)
    if data is None:
        crud.create_variables(db, **variables.dict())
    else:
        update_data = {k: (getattr(data, k) if v == "" else v) for k, v in variables.dict().items()}
        crud.update_variables(db, data.id, **update_data)
    return {"success": "true"}

@router.get('/timer')
async def get_timer(email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    data = crud.get_variables(db)
    if data is None:
        return None
    else:
        print(data.timer)
        return data.timer
        
        
    return {"success": "true"}

@router.get('/rerun-chatgpt')
async def rerun_chatgpt_route(email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    await update_notification()
    return {"success": "true"}



@router.get('/set-opt-in-status-email')
def set_opt_in_status_email(email: Annotated[str, Depends(get_current_user)], customer_id: int, opt_in_status_email: int, db: Session = Depends(get_db)):
    print("dashboard - customer_id: ", customer_id)
    customer = crud.get_customer(db, customer_id)
    send_opt_in_email(customer_id, customer.email, db)
    crud.update_opt_in_status_email(db, customer_id, opt_in_status_email)
    return True

@router.get('/set-opt-in-status-phone')
def set_opt_in_status_phone(email: Annotated[str, Depends(get_current_user)], customer_id: int, opt_in_status_phone: int, db: Session = Depends(get_db)):
    print("dashboard - customer_id: ", customer_id)
    customer = crud.get_customer(db, customer_id)
    send_opt_in_phone(customer.phone, db)
    crud.update_opt_in_status_phone(db, customer_id, opt_in_status_phone)
    return True

@router.get('/confirm-opt-in-status')
def set_opt_in_status(customer_id: int, response: str, db: Session = Depends(get_db)):
    print("dashboard - customer_id: ", customer_id)
    
    crud.update_opt_in_status_email(db, customer_id, 2 if response == "accept" else 3)
    if response == "accept":
        return "Sent Successfully! Congulatulations!"
    else:
        return "Sent Successfully!"
    

@router.post("/incoming-sms")
async def handle_sms(Body: str = Form(...), From: str = Form(...), db: Session = Depends(get_db)):
    # Convert message to uppercase for consistent matching
    incoming_msg = Body.strip().upper()
    From = From.replace(' ', '')
    print("dashboard - From: ", From)
    # Create a Twilio MessagingResponse object
    response = MessagingResponse()
    
    # Check if the incoming message is a recognized keyword
    if incoming_msg == "#STOP":
        customer = crud.find_customer_with_phone(db, From)
        if customer is not None:
            crud.update_opt_in_status_phone(db, customer.id, 3) # Set as Opt Out
        response.message("You have been unsubscribed from messages. Reply with #START to subscribe again.")
    elif incoming_msg == "#START":
        # Update your database to mark this number as opted-in
        customer = crud.find_customer_with_phone(db, From)
        if customer is not None:
            crud.update_opt_in_status_phone(db, customer.id, 2) # Set as Opt In
        response.message("You have been subscribed to messages.")
    else:
        # The message is not a recognized keyword
        response.message("Sorry, we did not understand your message. Reply with #STOP to unsubscribe or #START to subscribe.")

    # Return the response to Twilio
    return response.to_xml()


@router.get('/variables')
def get_variables(email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    
    data = crud.get_variables(db)
    return data

@router.get('/check-database-update')
def get_variables(email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    
    data = crud.get_variables(db)
    if data is None:
        return False
    
    db_update_status = data.db_update_status
    print("dashboard - data.db_update_status: ", data.db_update_status)
    
    if db_update_status:
        crud.set_db_update_status(db, data.id, 0)
        return True
    else:
        return False