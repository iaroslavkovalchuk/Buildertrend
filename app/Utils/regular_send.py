import os
from twilio.rest import Client

from dotenv import load_dotenv
from datetime import datetime, timedelta
from app.Utils.database_handler import DatabaseHandler
from app.Utils.sendgrid import send_mail
load_dotenv()

db = DatabaseHandler()

# def send_sms_via_email():


def send_sms_via_phone_number(phone_number: str, sms: str):
    
    # Fetch your Account SID and Auth Token from environment variables
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')

    # Initialize the Twilio client
    client = Client(account_sid, auth_token)

    # Your Twilio phone number (purchased from Twilio Console)
    twilio_number = os.getenv('TWILIO_PHONE_NUMBER')

    # Send the SMS
    message = client.messages.create(
        to=phone_number,
        from_=twilio_number,
        body=sms
    )

    # Optionally print the message SID
    if message.sid:
        return True
    else:
        return False
    
    
def send(project_id):
    project = db.get_project(project_id)
    sent_time = datetime.utcnow()
    customer = db.get_customer(project[2])
    phone_number = customer[4]
    if(db.check_duplicate_messgae(project[4]) == False): # check if it is duplicate message
        phone_sent_success = send_sms_via_phone_number(phone_number,  project[4]) # 4 means last_message
        email_sent_success = send_mail(project[4], "Update" ,project[3]) # 3 means email
        db.update_project_sent_status(project_id, phone_sent_success, email_sent_success)
    else:
        return False
    db.set_project_sent(project_id, 3, sent_time) # update function error
    db.insert_message_history(project[4], project_id)
    return True