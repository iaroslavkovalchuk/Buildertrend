# import os
# from twilio.rest import Client

# from dotenv import load_dotenv
# from datetime import datetime, timedelta
# import app.Utils.database_handler as crud
# from app.Utils.sendgrid import send_mail
# load_dotenv()

# # db = DatabaseHandler()

# variables = db.get_variables()

# def send_sms_via_phone_number(phone_number: str, sms: str):
    
#     # Fetch your Account SID and Auth Token from environment variables
#     account_sid = os.getenv('TWILIO_ACCOUNT_SID')
#     auth_token = os.getenv('TWILIO_AUTH_TOKEN')
#     twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
    
    
    
#     if variables is not None:
#         account_sid = variables[3]
#         auth_token = variables[4]
#         twilio_number = variables[2]

#     # Initialize the Twilio client
#     client = Client(account_sid, auth_token)

#     # Your Twilio phone number (purchased from Twilio Console)

#     # Send the SMS
#     print("phone number: ", phone_number)
#     message = client.messages.create(
#         to="+1 320 5471980",
#         from_=twilio_number,
#         body=sms
#     )
#     message = client.messages.create(
#         to=phone_number,
#         from_=twilio_number,
#         body=sms
#     )


#     # Optionally print the message SID
#     if message.sid:
#         return True
#     else:
#         return False
    
    
# def send(project_id):
#     project = db.get_project(project_id)
#     sent_time = datetime.utcnow()
#     customer = db.get_customer(project[2])
#     phone_number = customer[4]
#     phone_sent_success = 0
#     email_sent_success = 0
#     if(db.check_duplicate_messgae(project[4]) == False): # check if it is duplicate message
#         try:
#             phone_sent_success = send_sms_via_phone_number(phone_number,  project[4]) # 4 means last_message
#         except:
#             phone_sent_success = 0
#         try:
#             print("email: ", project[3])
#             email_sent_success = send_mail(project[4], "Update" ,customer[3]) # 3 means email
#         except:
#             email_sent_success = 0
#         db.update_project_sent_status(project_id, phone_sent_success, email_sent_success)
#     else:
#         db.update_project_sent_status(project_id, phone_sent_success, email_sent_success)
#         return False
    
#     print("phone_sent_success: ", phone_sent_success)
#     print("email_sent_success: ", email_sent_success)
#     db.set_project_sent(project_id, 3, sent_time) # update function error
#     db.insert_message_history(project[4], project_id)
#     return True