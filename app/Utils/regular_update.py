from app.Utils.database_handler import DatabaseHandler
from app.Utils.chatgpt import get_last_message
import requests
from datetime import datetime

def job():
    db_handler = DatabaseHandler()
    print("Scraping started!")
    response = requests.get('https://api.cultuurtickets.nl/buildertrend/api/v1/notification')
    response = response.json()
    print(response)
    for report in response:
        first_name = report['first_name']
        last_name = report['last_name']
        phone = report['phone']
        address = report['address']
        email = report['email']
        note_list = report['reports']
        print(report)
        # Insert the customer into the database and get the customer_id
        customer_id = db_handler.insert_customer(first_name, last_name, email, phone, address)
        send_method = db_handler.get_customer_send_method(customer_id)[0]
        print(send_method)
        # Insert the project into the database and get the project_id
        # Assuming claim_number is available in the report
        claim_number = report['claim_number'] 
        project_id = db_handler.insert_project(claim_number, customer_id)
        flag = 0

        db_handler.set_project_status(project_id, send_method, datetime.utcnow())
        
        # Insert each report into the database
        for message in note_list:
            flag = 1
            db_handler.insert_report(project_id, message['title'] + message['note'], message['date'])
        
        if flag == 1:
            # Get all reports in this claim
            reports_list = db_handler.get_report(project_id)
            # Get personalized message based on reports
            last_message = get_last_message(reports_list, first_name + ' ' + last_name)
            # Save message in this claim
            db_handler.set_project_message(project_id, last_message)
    print("DB updated!")