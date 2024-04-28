from sendgrid.helpers.mail import Mail, Email, To, Content
import sendgrid
import os
from dotenv import load_dotenv
load_dotenv()

sendgrid_client = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
from_mail = os.getenv("SENDGRID_FROM_EMAIL")

def send_mail(text: str, subject: str, to_email: str):
    try:
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