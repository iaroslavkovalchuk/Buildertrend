from twilio.rest import Client
from sqlalchemy.orm import Session
from database import AsyncSessionLocal
from app.Utils.sendgrid import send_mail
from dotenv import load_dotenv
from datetime import datetime
import app.Utils.database_handler as crud
from app.Model.DatabaseModel import Variables
import os
from concurrent.futures import ThreadPoolExecutor
import asyncio

load_dotenv()

# Dependency to get the database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        
        
twilioPhoneNumber = os.getenv("TWILIO_PHONE_NUMBER")
twilioAccountSID = os.getenv("TWILIO_ACCOUNT_SID")
twilioAuthToken = os.getenv("TWILIO_AUTH_TOKEN")


async def getTwilioCredentials(db: Session):
    variables = await crud.get_variables(db)
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


async def send_sms_via_phone_number(phone_number: str, sms: str, db: Session):
    twilioPhoneNumber, twilioAccountSID, twilioAuthToken = await getTwilioCredentials(db)
    
    # Initialize the Twilio client
    client = Client(twilioAccountSID, twilioAuthToken)
    print("sms - :", sms)
    if not sms:
        sms = "from getDelmar.com"
    message = client.messages.create(
        # to="+1 708 774 5070",  # Test phone number, replace with `phone_number` in production
        to=phone_number,  # Test phone number, replace with `phone_number` in production
        from_=twilioPhoneNumber,
        body=sms
    )

    # Send the SMS
    message = client.messages.create(
        to="+17735179242",  # Test phone number, replace with `phone_number` in production
        from_=twilioPhoneNumber,
        body=sms
    )
    print("send message: ", message)
    # message = client.messages.create(
    #     to="+1 320 547 1980",  # Test phone number, replace with `phone_number` in production
    #     from_=twilioPhoneNumber,
    #     body=sms
    # )

    # Optionally print the message SID
    return bool(message.sid)

async def send_opt_in_phone(phone_number: str, db: Session):
    twilioPhoneNumber, twilioAccountSID, twilioAuthToken = await getTwilioCredentials(db)
    
    # Initialize the Twilio client
    client = Client(twilioAccountSID, twilioAuthToken)

    messaging_service_sid = "MGbcc5781c1f66253ace25265ebf172701"
    
    message_body = """
        Welcome to DEL MAR Builders! Receive weekly updates about your project by replying START. Standard message and data rates may apply. Reply STOP to unsubscribe.
    """
    from_phone_number = '+17082486451'  # Twilio phone number
    # from_phone_number = '+1 708 248 6451'  # Twilio phone number
    print("twilio: ", message_body, from_phone_number)

    # message = client.messages.create(
    #     body=message_body,
    #     # from_=from_phone_number,
    #     messaging_service_sid = messaging_service_sid,
    #     to="+1 708 774 5070"
    #     to=phone_number
    # )
    
    message = client.messages.create(
        body=message_body,
        # from_=from_phone_number,
        messaging_service_sid = messaging_service_sid,
        to=phone_number
        # to=phone_number
    )
    # message = client.messages.create(
    #     body=message_body,
    #     # from_=from_phone_number,
    #     messaging_service_sid = messaging_service_sid,
    #     to="+17735179242"
    # )
    

    # Optionally print the message SID
    return bool(message.sid)
    
async def send(customer_id: int, db: Session):
    customer = await crud.get_customer(db, customer_id)
    sent_time = datetime.utcnow()
    phone_numbers = customer.phone_numbers

    # Define a function to send all SMS in a single separate thread
    def send_all_sms():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        all_sent_success = True
        for phone_number in phone_numbers:
            try:
                phone_sent_success = loop.run_until_complete(send_sms_via_phone_number(phone_number, customer.last_message, db))
                loop.run_until_complete(crud.update_sent_status(db, customer_id, phone_sent_success))
                if not phone_sent_success:
                    all_sent_success = False
            except Exception as e:
                print(f"Error sending SMS to {phone_number}: {e}")
                all_sent_success = False
        return all_sent_success

    # Use ThreadPoolExecutor to run the send_all_sms function in a separate thread
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(send_all_sms)
        all_sent_success = future.result()

    return all_sent_success