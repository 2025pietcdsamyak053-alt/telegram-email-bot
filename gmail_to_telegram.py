from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests

BOT_TOKEN = "8959866163:AAEFR5oQY8lYP_RmE5o7hbvadLu2wap1GU8"
CHAT_ID = "5155133339"

creds = Credentials.from_authorized_user_file("token.json")
service = build("gmail", "v1", credentials=creds)

results = service.users().messages().list(
    userId="me",
    maxResults=1
).execute()

messages = results.get("messages", [])

if messages:
    msg = service.users().messages().get(
        userId="me",
        id=messages[0]["id"]
    ).execute()

    headers = msg["payload"]["headers"]

    subject = "No Subject"
    sender = "Unknown"

    for h in headers:
        if h["name"] == "Subject":
            subject = h["value"]
        elif h["name"] == "From":
            sender = h["value"]

    text = f"📧 New Email\n\n👤 From: {sender}\n\n📌 Subject: {subject}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

    print("Email sent to Telegram!")