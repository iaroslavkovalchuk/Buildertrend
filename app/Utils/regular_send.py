from twilio.rest import Client
from sqlalchemy.orm import Session
from database import SessionLocal
from app.Utils.sendgrid import send_mail
from dotenv import load_dotenv
from datetime import datetime
import app.Utils.database_handler as crud
from app.Model.DatabaseModel import Variables
import os

load_dotenv()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
twilioPhoneNumber = os.getenv("TWILIO_PHONE_NUMBER")
twilioAccountSID = os.getenv("TWILIO_ACCOUNT_SID")
twilioAuthToken = os.getenv("TWILIO_AUTH_TOKEN")


def getTwilioCredentials(db: Session):
    variables = crud.get_variables(db)
    number = ''
    sid = ''
    token = ''
    if variables:
        number = variables.twilioPhoneNumber or twilioPhoneNumber
        sid = variables.twilioAccountSID or twilioAccountSID
        token = variables.twilioAuthToken or twilioAuthToken
    else:
        number = twilioPhoneNumber
        sid = twilioAccountSID
        token = twilioAuthToken
    return number, sid, token


def send_sms_via_phone_number(phone_number: str, sms: str, db: Session):
    twilioPhoneNumber, twilioAccountSID, twilioAuthToken = getTwilioCredentials(db)
    
    # Initialize the Twilio client
    client = Client(twilioAccountSID, twilioAuthToken)

    # Send the SMS
    message = client.messages.create(
        to="+1 320 5471980",  # Test phone number, replace with `phone_number` in production
        from_=twilioPhoneNumber,
        body=sms
    )

    # Optionally print the message SID
    return bool(message.sid)
    
def send(project_id: int, db: Session):
    project = crud.get_project(db, project_id)
    sent_time = datetime.utcnow()
    customer = crud.get_customer(db, project.customer_id)
    phone_number = customer.phone
    phone_sent_success = False
    email_sent_success = False
    
    
    print("phone_number: ", phone_number)
    print("email: ", customer.email)
    print("phone_number: ", phone_number)
    # return True
    
    if not crud.check_duplicate_message(db, project.last_message):  # check if it is a duplicate message
        try:
            phone_sent_success = send_sms_via_phone_number(phone_number, project.last_message, db)
        except Exception as e:
            print(f"Error sending SMS: {e}")
            phone_sent_success = False
        try:
            email_sent_success = send_mail(project.last_message, "Update", customer.email)
        except Exception as e:
            print(f"Error sending email: {e}")
            email_sent_success = False
        crud.update_project_sent_status(db, project_id, phone_sent_success, email_sent_success)
    else:
        crud.update_project_sent_status(db, project_id, phone_sent_success, email_sent_success)
        return False
    
    print("phone_sent_success: ", phone_sent_success)
    print("email_sent_success: ", email_sent_success)
    crud.set_project_sent(db, project_id, 3, sent_time)
    crud.insert_message_history(db, project.last_message, project_id)
    return True
