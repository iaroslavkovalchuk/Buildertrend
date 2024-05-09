from app.Utils.database_handler import DatabaseHandler
from app.Utils.chatgpt import get_last_message
import requests
from datetime import datetime
from pydantic import BaseModel

class AuthModel(BaseModel):
    builder_user: str
    builder_pass: str
    xact_user: str
    xact_pass: str

def job():
    db_handler = DatabaseHandler()
    print("Scraping started!")

    # Create an instance of AuthModel with your credentials
    auth_data = AuthModel(
        builder_user='Angelab@getdelmar.com',
        builder_pass='Liamb0218.',
        xact_user='Angelab@getdelmar.com',
        xact_pass='Liamb0218$'
    )
    
    json_data = auth_data.dict()
    
    response = requests.post('https://api.cultuurtickets.nl/buildertrend/api/v1/notification', json = json_data)
    response = response.json()
    print(response)
    for report in response:
        try:
            first_name = report['first_name']
            last_name = report['last_name']
            phone = report['phone']
            address = report['address']
            email = report['email']
            note_list = report['reports']
            claim_number = report['claim_number']
            project_name = report['project_name']
            # print(report)
            print("first_name: ", first_name)
            print("last_name: ", last_name)
            print('project_name: ', report['project_name'])
            print('claim_number: ', report['claim_number'])
            
            # continue
            # Insert the customer into the database and get the customer_id
            customer_id = db_handler.insert_customer(first_name, last_name, email, phone, address)
            send_method = db_handler.get_customer_send_method(customer_id)[0]
            print(send_method)
            
            # Insert the project into the database and get the project_id
            project_id = db_handler.insert_project(claim_number, customer_id, project_name)
            flag = 0
            print("project_id: ", project_id)
            
            db_handler.set_project_status(project_id, send_method, datetime.utcnow())
            
            # Insert each report into the database
            for message in note_list:
                flag = 1
                try:
                    db_handler.insert_report(project_id, message['title'] + message['note'], message['date'])
                except Exception as e:
                    print("------------------------------------------")
                    print(project_id, "--\n", message['title'] + message['note'], message['date'])
                    print('===')
                    print(e)
                    print("------------------------------------------")
            
            if flag == 1:
                # Get all reports in this claim
                try:
                    reports_list = db_handler.get_report(project_id)
                    # Get personalized message based on reports
                    last_message = get_last_message(reports_list, first_name + ' ' + last_name)
                    # Save message in this claim
                    db_handler.set_project_message(project_id, last_message)
                except Exception as e:
                    print('++++++++++++++++++++++++++++++++++++++')
                    print(project_id)
                    print(e)
                    print('+++++++++++++++++++++++++++++++++++++++')
        except Exception as e:
            print(e)
    print("DB updated!")
    