from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests
import time

BOT_TOKEN = "8959866163:AAEFR5oQY8lYP_RmE5o7hbvadLu2wap1GU8"
CHAT_ID = "5155133339"

creds = Credentials.from_authorized_user_file("token.json")
service = build("gmail", "v1", credentials=creds)

last_email_id = None

while True:
    try:
        results = service.users().messages().list(
            userId="me",
            maxResults=1
        ).execute()

        messages = results.get("messages", [])

        if messages:
            current_id = messages[0]["id"]

            if current_id != last_email_id:
                last_email_id = current_id

                msg = service.users().messages().get(
                    userId="me",
                    id=current_id
                ).execute()

                subject = "No Subject"
                sender = "Unknown"

                for h in msg["payload"]["headers"]:
                    if h["name"] == "Subject":
                        subject = h["value"]
                    elif h["name"] == "From":
                        sender = h["value"]

                text = f"📧 New Email\n\n👤 From: {sender}\n\n📌 Subject: {subject}"

                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    data={
                        "chat_id": CHAT_ID,
                        "text": text
                    }
                )

                print("New email sent!")

        time.sleep(30)

    except Exception as e:
        print("Error:", e)
        time.sleep(30)