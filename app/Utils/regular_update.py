from sqlalchemy.orm import Session
from database import SessionLocal
import app.Utils.database_handler as crud
from app.Utils.chatgpt import get_last_message
import requests
from datetime import datetime
from pydantic import BaseModel

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

async def update_notification():
    db = SessionLocal()
    # project_list = crud.get_all_projects(db)
    # print('regular_update - project_list: ', project_list)
    # count = 0
    # for project in project_list:
    #     count += 1
    #     print("regular_update - customer_id: ", project.customer_id)
    #     print("regular_update - project_id: ", project.id)
    #     customer = crud.get_customer(db, project.customer_id)
    #     reports_list = crud.get_reports_by_project_id(db, project.id)
    #     # Get personalized message based on reports
    #     last_message = get_last_message(db, reports_list, customer.first_name + ' ' + customer.last_name)
    #     crud.update_project(db, project.id, last_message=last_message)

    variables = crud.get_variables(db)
    if variables is not None:
        crud.set_db_update_status(db, variables.id, 1)

def update_database(data):    
    # Start a new SQLAlchemy session
    db = SessionLocal()
    
    for report in data:
        try:
            first_name = report['first_name']
            last_name = report['last_name']
            phone = report['phone']
            phone = phone.replace(" ", "")
            if len(phone) < 5:
                phone = ""
            address = report['address']
            email = report['email']
            note_list = report['reports']
            claim_number = report['claim_number']
            project_name = report['project_name']
            
            # Insert the customer into the database and get the customer_id
            customer = crud.insert_customer(db, first_name, last_name, email, phone, address)
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
                    crud.insert_report(db, project.id, message['title'] + message['note'] + '\n' + message['date'], message['date'])
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
                    last_message = get_last_message(db, reports_list, first_name + ' ' + last_name)
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

    print("DB updated!")
    
    variables = crud.get_variables(db)
    if variables is not None:
        crud.set_db_update_status(db, variables.id, 1)
    # db.close()