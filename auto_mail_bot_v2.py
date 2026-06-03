from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests
import base64
import os
import time

BOT_TOKEN = "8959866163:AAEFR5oQY8lYP_RmE5o7hbvadLu2wap1GU8"
CHAT_ID = "5155133339"

LAST_EMAIL_FILE = "last_email.txt"

creds = Credentials.from_authorized_user_file("token.json")
service = build("gmail", "v1", credentials=creds)

print("Bot Started...")
print("Checking Gmail every 30 seconds...")

def get_body(payload):

    if "parts" in payload:
        for part in payload["parts"]:
            result = get_body(part)

            if result:
                return result

    if payload.get("mimeType") == "text/plain":

        data = payload.get("body", {}).get("data")

        if data:
            return base64.urlsafe_b64decode(
                data
            ).decode(
                "utf-8",
                errors="ignore"
            )

    return None


def send_pdf(parts, message_id):

    for part in parts:

        filename = part.get("filename", "")

        if filename.endswith(".pdf"):

            attachment_id = part["body"]["attachmentId"]

            attachment = service.users().messages().attachments().get(
                userId="me",
                messageId=message_id,
                id=attachment_id
            ).execute()

            file_data = base64.urlsafe_b64decode(
                attachment["data"]
            )

            with open(filename, "wb") as f:
                f.write(file_data)

            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                data={
                    "chat_id": CHAT_ID
                },
                files={
                    "document": open(filename, "rb")
                }
            )

            print("PDF Sent:", filename)

        if "parts" in part:
            send_pdf(part["parts"], message_id)


while True:

    try:

        results = service.users().messages().list(
            userId="me",
            maxResults=1
        ).execute()

        messages = results.get("messages", [])

        if not messages:
            print("No emails found")
            time.sleep(30)
            continue

        email_id = messages[0]["id"]

        last_email_id = ""

        if os.path.exists(LAST_EMAIL_FILE):
            with open(LAST_EMAIL_FILE, "r") as f:
                last_email_id = f.read().strip()

        if email_id == last_email_id:
            print("No new email")
            time.sleep(30)
            continue

        msg = service.users().messages().get(
            userId="me",
            id=email_id,
            format="full"
        ).execute()

        headers = msg["payload"]["headers"]

        subject = "No Subject"
        sender = "Unknown"

        for h in headers:
            if h["name"] == "Subject":
                subject = h["value"]

            elif h["name"] == "From":
                sender = h["value"]

        body = "Body not found"

        extracted_body = get_body(msg["payload"])

        if extracted_body:
            body = extracted_body

        text = f"""📧 New Email

👤 From: {sender}

📌 Subject: {subject}

📝 Body:

{body[:3000]}
"""

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text
            }
        )

        print("Email Sent!")

        if "parts" in msg["payload"]:
            send_pdf(
                msg["payload"]["parts"],
                msg["id"]
            )

        with open(LAST_EMAIL_FILE, "w") as f:
            f.write(email_id)

    except Exception as e:
        print("Error:", e)

    time.sleep(30)