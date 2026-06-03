from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64

creds = Credentials.from_authorized_user_file("token.json")

service = build("gmail", "v1", credentials=creds)

results = service.users().messages().list(
    userId="me",
    maxResults=5
).execute()

messages = results.get("messages", [])

if not messages:
    print("No emails found.")
else:
    for msg in messages:
        txt = service.users().messages().get(
            userId="me",
            id=msg["id"]
        ).execute()

        headers = txt["payload"]["headers"]

        subject = "No Subject"
        sender = "Unknown"

        for h in headers:
            if h["name"] == "Subject":
                subject = h["value"]
            if h["name"] == "From":
                sender = h["value"]

        print("\n-------------------")
        print("From:", sender)
        print("Subject:", subject)