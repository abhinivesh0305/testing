import os
import time
import requests
import json
import msal
def communicate(subject, sender_email, recipient_email, body, attachments=None):
    CLIENT_ID = os.getenv("CLIENT_ID")
    TENANT_ID = os.getenv("TENANT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    def get_access_token():
        token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": "https://graph.microsoft.com/.default",
        }
        response = requests.post(token_url, data=data, timeout=15)
        if response.status_code == 200:
            return response.json().get("access_token")
        raise requests.exceptions.RequestException("Failed to acquire access token.")

    access_token = get_access_token()
    if not access_token:
        print("Failed to acquire access token")
        return

    graph_url = f"https://graph.microsoft.com/v1.0/users/{sender_email}/sendMail"

    email_message = {
        "message": {
            "from": {"emailAddress": {"address": sender_email}},
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": [{"emailAddress": {"address": recipient_email}}],
        },
        "saveToSentItems": "true",
    }

    if attachments:
        email_message["message"]["attachments"] = [
            {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": attachment["name"],
                "contentBytes": attachment["contentBytes"]
            }
            for attachment in attachments
        ]

    response = requests.post(
        graph_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        data=json.dumps(email_message),
    )

    if response.status_code == 202:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email. Status code: {response.status_code}")
        print(response.text)