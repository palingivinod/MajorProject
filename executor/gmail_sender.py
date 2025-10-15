# import base64
# from email.mime.text import MIMEText
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# import os
# import pickle

# SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# def get_gmail_service():
#     creds = None
#     # token.pickle stores the user access/refresh tokens
#     if os.path.exists('config/token.pickle'):
#         with open('config/token.pickle', 'rb') as token:
#             creds = pickle.load(token)
#     # If no valid credentials, do OAuth flow
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'config/credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for next run
#         with open('config/token.pickle', 'wb') as token:
#             pickle.dump(creds, token)

#     service = build('gmail', 'v1', credentials=creds)
#     return service

# def send_email(slots):
#     """
#     slots = {
#         "to": "recipient_email_or_name",
#         "body": "message content",
#         "subject": "optional subject"
#     }
#     """
#     service = get_gmail_service()
#     to_email = slots.get("to")
#     body = slots.get("body", "No content provided.")
#     subject = slots.get("subject", "Message from Voice Assistant")

#     message = MIMEText(body)
#     message['to'] = to_email
#     message['subject'] = subject

#     raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

#     try:
#         sent_message = service.users().messages().send(
#             userId='me', body={'raw': raw}).execute()
#         return f"✅ Email sent to {to_email}! (ID: {sent_message['id']})"
#     except Exception as e:
#         return f"⚠️ Failed to send email: {e}"




import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.contacts import CONTACTS  # your contact mapping
from datetime import datetime
import json

# Load your credentials from a JSON or settings file
with open("credentials.json") as f:
    creds = json.load(f)
EMAIL_ADDRESS = creds.get("email")  # your Gmail address
EMAIL_PASSWORD = creds.get("app_password")  # app password, NOT your normal Gmail password

def format_subject(body):
    """Generate a subject line automatically if not provided."""
    keywords = ["report", "project", "meeting", "update", "task"]
    for word in keywords:
        if word in body.lower():
            return f"{word.capitalize()} Update - {datetime.now().strftime('%b %d, %Y')}"
    return f"Message from Voice Assistant - {datetime.now().strftime('%b %d, %Y')}"

def send_email(slots):
    """
    slots should be a dict with keys: 'to', 'body', optionally 'subject'
    """
    try:
        to_name = slots.get("to", "").lower()
        body = slots.get("body", "").strip()
        subject = slots.get("subject", "").strip()

        # Find recipient email
        recipient_email = CONTACTS.get(to_name, to_name)
        if not recipient_email:
            return "❌ Recipient not found. Provide a valid name or email."

        # Generate subject if missing
        if not subject:
            subject = format_subject(body)
        if not body:
            body = "No message content provided."

        # Create message
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect and send
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return f"✅ Email sent to {to_name.title()} ({recipient_email})!"

    except Exception as e:
        return f"⚠️ Failed to send email: {e}"
