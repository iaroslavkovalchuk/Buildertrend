from sqlalchemy.orm import Session
from database import SessionLocal
import app.Utils.database_handler as crud
from app.Utils.chatgpt import get_last_message
import requests
from datetime import datetime
from pydantic import BaseModel
import time
class AuthModel(BaseModel):
    source: str
    builder_user: str
    builder_pass: str
    xact_user: str
    xact_pass: str

def job(source: str):
    print("Scraping started!")

    # Create an instance of AuthModel with your credentials
    auth_data = AuthModel(
        source=source,
        builder_user='Angelab@getdelmar.com',
        builder_pass='Liamb0218.',
        xact_user='Angelab@getdelmar.com',
        xact_pass='Liamb0218$'
    )
    
    json_data = auth_data.dict()
    print(source)
    response = requests.post('https://api.cultuurtickets.nl/buildertrend/api/v1/notification', json=json_data)
    return


def process_phone_number(phone):
    phone.replace(" ", "")
    if len(phone) < 5:
        return ""
    phone.replace('(', '')
    phone.replace(')', '')
    phone.replace('-', '')
    phone.replace('.', '')
    if '+' in phone:
        return phone
    else:
        return '+1' + phone
        

def update_notification(db: Session):
    project_list = crud.get_all_projects(db)
    print('regular_update - project_list: ', project_list)
    count = 0
    status = crud.get_status(db)
    if status is not None:
        crud.update_rerun_status(db, status.id, len(project_list), count)
    for project in project_list:
        count += 1
        print("regular_update - customer_id: ", project.customer_id)
        print("regular_update - project_id: ", project.id)
        customer = crud.get_customer(db, project.customer_id)
        reports_list = crud.get_reports_by_project_id(db, project.id)
        # Get personalized message based on reports
        # last_message = get_last_message(db, customer.manager_name, customer.manager_phone, customer.manager_email, reports_list, customer.first_name + ' ' + customer.last_name)
        # crud.update_project(db, project.id, last_message=last_message)
        time.sleep(1)
        if status is not None:
            crud.update_rerun_status(db, status.id, len(project_list), count)

    if status is not None:
        crud.set_db_update_status(db, status.id, 1)

def update_database(data):    
    # Start a new SQLAlchemy session
    db = SessionLocal()
    status = crud.get_status(db)
    project_total = len(data)
    project_current = 0
    if status is not None:
        crud.update_rerun_status(db, status.id, project_total, project_current)
    
    for report in data:
        project_current += 1
        try:
            first_name = report['first_name'].capitalize()
            last_name = report['last_name'].capitalize()
            phone = report['phone']
            phone = process_phone_number(phone)
            print("phone: ", phone)
            address = report['address']
            email = report['email']
            note_list = report['reports']
            claim_number = report['claim_number']
            project_name = report['project_name']
            manager_name = report['manager_name']
            manager_phone = report['manager_phone']
            manager_phone = process_phone_number(manager_phone)
            manager_email = report['manager_email']
            
            # Insert the customer into the database and get the customer_id
            customer = crud.insert_customer(db,  manager_name, manager_phone, manager_email, first_name, last_name, email, phone, address)
            send_method = customer.sending_method
            print("regular_update - send_method: ", send_method)
            print("regular_update - customer_id: ", customer.id)
            
            # Insert the project into the database and get the project_id
            project = crud.insert_project(db, claim_number, customer.id, project_name)
            print("project_id: ", project.id)
            
            crud.update_project(db, project.id, message_status=send_method, qued_timestamp=datetime.utcnow())
            
            flag = 0
            # Insert each report into the database
            for message in note_list:
                print('++++++++++++++++++++++++++++++++++++++')
                print(project.id, "--\n", message['title'] + message['note'])
                print('++++++++++++++++++++++++++++++++++++++')
                flag = 1
                try:
                    crud.insert_report(db, project.id, message['title'] + '\n' + message['note'] + '\n' + message['date'], message['date'])
                except Exception as e:
                    print("------------------------------------------")
                    print(project.id, "--\n", message['title'] + message['note'])
                    print('===')
                    print(e)
                    print("------------------------------------------")
            print('regular_update - flag', flag)
            if flag == 1:
                # Get all reports in this claim
                try:
                    reports_list = crud.get_reports_by_project_id(db, project.id)
                    # Get personalized message based on reports
                    print("reposts_list: ", reports_list)
                    last_message = get_last_message(db, manager_name, manager_phone, manager_email, reports_list, first_name + ' ' + last_name)
                    print('regular_update - last_message: ', last_message)
                    # Save message in this claim
                    crud.update_project(db, project.id, last_message=last_message)
                    
                except Exception as e:
                    print('++++++++++++++++++++++++++++++++++++++')
                    print(project.id)
                    print(e)
                    print('+++++++++++++++++++++++++++++++++++++++')
        except Exception as e:
            print(e)
        if status is not None:
            crud.update_rerun_status(db, status.id, project_total, project_current)
    print("DB updated!")
    
    variables = crud.get_variables(db)
    if variables is not None:
        crud.set_db_update_status(db, variables.id, 1)
    # db.close()