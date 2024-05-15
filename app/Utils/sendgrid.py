from sendgrid.helpers.mail import Mail, Email, To, Content
from sendgrid import SendGridAPIClient
from sqlalchemy.orm import Session
from database import SessionLocal
import app.Utils.database_handler as crud
import os

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
sendgrid_from_email = os.getenv("SENDGRID_FROM_EMAIL")


def get_api_key_and_from_mail(db: Session):
    # Retrieve variables from the database using CRUD operations
    variables = crud.get_variables(db)
    api_key = ''
    from_mail = ''
    if variables:
        api_key = variables.sendgridApiKey or sendgrid_api_key
        from_mail = variables.sendgridEmail or sendgrid_from_email
    else:
        api_key = sendgrid_api_key
        from_mail = sendgrid_from_email
    return api_key, from_mail


def send_mail(text: str, subject: str, to_email: str, db: Session):
    try:
        api_key, from_mail = get_api_key_and_from_mail(db)

        sendgrid_client = SendGridAPIClient(api_key=api_key)

        to_email = "serhiivernyhora@outlook.com"

        from_email_obj = Email(from_mail)  # Change to your verified sender
        to_email_obj = To(to_email)  # Change to your recipient
        content = Content("text/plain", text)
        mail = Mail(from_email_obj, to_email_obj, subject, content)
        mail_json = mail.get()
        
        # Send an HTTP POST request to /mail/send
        response = sendgrid_client.client.mail.send.post(request_body=mail_json)
        if response.status_code == 202:
            return True
        else:
            return False
    except Exception as e:
        print(f"Send mail Error: {e}")
        return False
