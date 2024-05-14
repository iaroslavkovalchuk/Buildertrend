from sendgrid.helpers.mail import Mail, Email, To, Content
import sendgrid
import os
from dotenv import load_dotenv
from app.Utils.database_handler import DatabaseHandler

load_dotenv()
db = DatabaseHandler()
variables = db.get_variables()

from_mail = os.getenv("SENDGRID_FROM_EMAIL")
api_key = os.getenv('SENDGRID_API_KEY')

if variables is not None:
    from_mail = variables[5]
    api_key = variables[6]

sendgrid_client = sendgrid.SendGridAPIClient(api_key=api_key)


def send_mail(text: str, subject: str, to_email: str):
    try:
        # to_email = "serhiivernyhora@outlook.com"
        from_email_obj = Email(from_mail)  # Change to your verified sender
        to_email_obj = To(to_email)  # Change to your recipient
        content = Content("text/plain", text)
        
        mail = Mail(from_email_obj, to_email_obj, subject, content)

        # Get a JSON-ready representation of the Mail object
        mail_json = mail.get()

        # Send an HTTP POST request to /mail/send
        response = sendgrid_client.client.mail.send.post(
            request_body=mail_json)
        if response.status_code == 202:
            return True
        else:
            return False
    except Exception as e:
        print(f"Send mail Error: {e}")
        # return HTTPException(status_code=500, detail={"error": e})
        return False