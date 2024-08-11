from fastapi import FastAPI,BackgroundTasks, APIRouter, Depends, HTTPException, status, File, UploadFile, Request, Form, Response
from fastapi.responses import FileResponse
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

@router.get('/update-db')
async def update_db(source: str, email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    print("dashboard - source: ", source)
    status = await crud.get_status(db)
    update_status = {}
    if source == "BuilderTrend":
        update_status = ScrapingStatusModel(buildertrend_total=status.buildertrend_total, buildertrend_current=0, xactanalysis_total=status.xactanalysis_total, xactanalysis_current=status.xactanalysis_current).dict()
    else:
        update_status = ScrapingStatusModel(buildertrend_total=status.buildertrend_total, buildertrend_current=status.buildertrend_current, xactanalysis_total=status.xactanalysis_total, xactanalysis_current=0).dict()
    print("**update_status: ", update_status)
    await crud.update_status(db, status.id, **update_status)
    
    await job(source)
    return True

@router.post('/get-scraped-result')
async def scraped_result(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    data = await request.json()
    print("dashboard - data: ", data)
    await update_database(data)
    # Process the raw JSON data here
    return {"received": len(data), "message": "Raw data processed successfully"}

@router.get('/table')
async def get_table(currentTab: int, email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    print("currentTab: ", currentTab)
    main_table_data = await crud.get_main_table(db)  # Replace with appropriate await crud operation
    
    # print("main_table_data: ", main_table_data)
    result = []
    for item in main_table_data:
        if item.is_deleted != currentTab:
            continue
        print("id ------", item.project_id)
        if not item.project_id:
            continue
        dict_item = item._asdict()
        if dict_item['message_status'] != 3:
            result.append(dict_item)
    
    send_result = []
    history_messages = await crud.get_all_message_history(db)
    for history_message in history_messages:
        sent_item = await crud.get_project(db, history_message.project_id)
        if sent_item:
            sent_item = {column.name: getattr(sent_item, column.name) for column in sent_item.__table__.columns}
        else:
            continue
        
        customer = await crud.get_customer(db, sent_item['customer_id'])
        if not customer:
            continue
        if customer.is_deleted != currentTab:
            continue
        
        sent_item['customer_id'] = customer.id
        sent_item['first_name'] = customer.first_name
        sent_item['last_name'] = customer.last_name
        sent_item['phone'] = customer.phone
        sent_item['email'] = customer.email
        sent_item['opt_in_status_email'] = customer.opt_in_status_email
        sent_item['opt_in_status_phone'] = customer.opt_in_status_phone
        sent_item['sending_method'] = customer.sending_method
        sent_item['is_deleted'] = customer.is_deleted
        sent_item['last_message'] = history_message.message
        sent_item['message_status'] = 3
        sent_item['sent_timestamp'] = history_message.sent_time
        sent_item['project_id'] = uuid.uuid4().int
        sent_item['history_id'] = history_message.id
        send_result.append(sent_item)
        # print("tmp_item: ", sent_item)
    send_result.reverse()
    print("len: ", len(send_result))
    result.extend(send_result)
            
    return result

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

@router.get('/download-project-message')
async def download_project_message(email: Annotated[str, Depends(get_current_user)], project_id: int, db: Session = Depends(get_db)):
    message = await crud.get_message_history_by_project_id(db, project_id)
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


@router.get('/delete-project')
async def delete_project(email: Annotated[str, Depends(get_current_user)], project_id: int, db: Session = Depends(get_db)):
    await crud.delete_project(db, project_id)


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

@router.get('/delete-customer')
async def delete_customer_route(email: Annotated[str, Depends(get_current_user)], customer_id: int, db: Session = Depends(get_db)):
    await crud.delete_customer(db, customer_id)
    return {"success": "true"}

@router.get('/restore-customer')
async def restore_customer_route(email: Annotated[str, Depends(get_current_user)], customer_id: int, db: Session = Depends(get_db)):
    await crud.restore_customer(db, customer_id)
    return {"success": "true"}

@router.get('/send')
async def send_message_route(email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    send()
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

@router.get('/rerun-chatgpt')
async def rerun_chatgpt_route(email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    # background_tasks.add_task(update_notification, db)
    await update_notification(db)
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
    

@router.post("/incoming-sms")
async def handle_sms(Body: str = Form(...), From: str = Form(...), db: Session = Depends(get_db)):
    # Convert message to uppercase for consistent matching
    incoming_msg = Body.strip().upper()
    From = From.replace(' ', '')
    print("dashboard - From: ", From)
    # Create a Twilio MessagingResponse object
    response = MessagingResponse()
    
    # Check if the incoming message is a recognized keyword
    if incoming_msg == "#STOP" or incoming_msg == "STOP":
        print("dashboard - incoming_msg:", incoming_msg)
        customer = await crud.find_customer_with_phone(db, From)
        if customer is not None:
            await crud.update_opt_in_status_phone(db, customer.id, 3) # Set as Opt Out
        response.message("You have been unsubscribed from messages. Reply with #START to subscribe again.")
        
    elif incoming_msg == "#START" or incoming_msg == "START" :
        print("dashboard - incoming_msg:", incoming_msg)
        # Update your database to mark this number as opted-in
        customer = await crud.find_customer_with_phone(db, From)
        print("dashboard - From:", From)
        print("dashboard - customer:", customer.id)
        if customer is not None:
            await crud.update_opt_in_status_phone(db, customer.id, 2) # Set as Opt In
        response.message("You have been subscribed to messages.")
        
    else:
        print("dashboard - incoming_msg:", incoming_msg)
        # The message is not a recognized keyword
        response.message("Sorry, we did not understand your message. Reply with #STOP to unsubscribe or #START to subscribe.")

    data = await crud.get_status(db)
    if data is not None:
        await crud.set_db_update_status(db, data.id, 1)

    # Return the response to Twilio
    print("dashboard - response: ", response)
    return Response(content=str(response), media_type="application/xml")


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


@router.post("/update-scraping-status")
async def update_scraping_status(scraping_status: ScrapingStatusModel, db: Session = Depends(get_db)):
    status = await crud.get_status(db)
    print("scraping_status: ", scraping_status)
    if status is not None:
        update_status = {k: (getattr(status, k) if v == -1 else v) for k, v in scraping_status.dict().items()}
        await crud.update_status(db, status.id, **update_status)
    return {"success": "true"}


@router.get("/check-scraping-status")
async def check_scraping_status(db: Session = Depends(get_db)):
    status = await crud.get_status(db)
    return status