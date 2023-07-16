import os.path
import base64
import json
import re
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging
import requests
import re
from googleapiclient.http import MediaFileUpload
import mlfiles
import os
import subprocess
from google.auth.exceptions import RefreshError
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify']

def readEmails(label="INBOX"):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(               
                # your creds file here. Please create json file as here https://cloud.google.com/docs/authentication/getting-started
                'my_cred_file.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=[label], q="is:unread").execute()
        messages = results.get('messages',[]);
        if not messages:
            print('No new messages.')
        else:
            message_count = 0
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()                
                email_data = msg['payload']['headers']
                for values in email_data:
                    name = values['name']
                    if name == 'From':
                        from_name= values['value']                
                        for part in msg['payload']['parts']:
                            try:
                                data = part['body']["data"]
                                byte_code = base64.urlsafe_b64decode(data)

                                text = byte_code.decode("utf-8")
                                print ("This is the message: "+ str(text))

                                # mark the message as read (optional)
                                msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()                                                       
                            except BaseException as error:
                                pass                            
    except Exception as error:
        print(f'An error occurred: {error}')


def get_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(               
                # your creds file here. Please create json file as here https://cloud.google.com/docs/authentication/getting-started
                'my_cred_file.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def mark_email_as_read(msg_id, service = get_service(), userId = 'me'):
    msg = service.users().messages().modify(userId=userId, id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()                                                       
    return msg

def get_email_body(payload):
    parts = payload.get('parts')
    body = ''
    if parts:
        for part in parts:
            mimeType = part.get('mimeType')
            if mimeType == 'text/plain':
                data = part['body'].get('data')
                if data:
                    byte_code = base64.urlsafe_b64decode(data)
                    body += byte_code.decode('utf-8')
            else:
                body += get_email_body(part)
    return body


def clean_body(email_body):
    regex = r"(?<=To:)(.*)(?=Subject:)"
    pattern = r"To:(.*?)Subject:"
    # Replace "To:" line with an empty string
    text = re.sub(regex, '', email_body, flags=re.S)
    text = re.sub(pattern, '', text, flags=re.S)
    return text



def get_unread_emails_with_label(label_name, folder_id):
    # Set up the Gmail API credentials
    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json')
        except RefreshError:
            os.remove('token.json')
            subprocess.call(['python', 'quickstart.py'])
            creds = Credentials.from_authorized_user_file('token.json')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/drive'])
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Create the Gmail API service
    service = build('gmail', 'v1', credentials=creds)

    # Create the Google Drive API service
    drive_service = build('drive', 'v3', credentials=creds)

    # Get the list of labels
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    # Check if the given label exists
    label_ids = []
    for lbl in labels:
        if lbl['name'] == label_name:
            label_ids.append(lbl['id'])
            break

    if not label_ids:
        print(f"Label '{label_name}' not found.")
        return []

    # Get the list of messages with the given label
    results = service.users().messages().list(
        userId='me', labelIds=label_ids, q="is:unread").execute()
    messages = results.get('messages', [])

    if not messages:
        print(f"No unread emails found with the label '{label_name}'.")
        return []

    unread_emails = []
    for message in messages:
        msg = service.users().messages().get(
            userId='me', id=message['id'], format='full').execute()
        payload = msg['payload']
        headers = payload['headers']
        subject = next(
            (header['value'] for header in headers if header['name'] == 'Subject'), '')
        sender = next(
            (header['value'] for header in headers if header['name'] == 'From'), '')
        date = next(
            (header['value'] for header in headers if header['name'] == 'Date'), '')
        msg_id = msg['id']
        body = get_email_body(payload)
        attachments = save_attachments_to_drive(service, drive_service, msg_id, folder_id)
        email = {
            'subject': subject,
            'sender': sender,
            'date': date,
            'message_id': msg_id,
            'body': remove_repeat_newlines(clean_body(body)),
            'attachments': attachments
        }
        unread_emails.append(email)

    return unread_emails






def save_attachments_to_drive(service, drive_service, message_id, folder_id):  # Add folder_id argument
    attachments = []
    msg = service.users().messages().get(userId='me', id=message_id).execute()
    parts = msg['payload']['parts']; # Create the 'attachments' directory if it doesn't exist
    os.makedirs('attachments', exist_ok=True)
    for part in parts:
        if part.get('filename'):
            file_data = service.users().messages().attachments().get(
                userId='me', messageId=message_id, id=part['body']['attachmentId']).execute()
            file_content = base64.urlsafe_b64decode(file_data['data'])

            # Save the attachment locally
            file_path = os.path.join('attachments', part['filename'])
            with open(file_path, 'wb') as f:
                f.write(file_content)

            # Upload the attachment to Google Drive
            drive_file = upload_file_to_drive(drive_service, part['filename'], file_path, folder_id) # Add folder_id here

            # Delete the local file
            os.remove(file_path)

            attachments.append(drive_file)

    return attachments



def upload_file_to_drive(drive_service, filename, file_path, folder_id):
    file_metadata = {
        'name': filename,
        'parents': [folder_id]  # add the folder_id to the file_metadata
    }
    media = MediaFileUpload(file_path, resumable=True)
    drive_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()
    return {
        'name': filename,
        'id': drive_file['id'],
        'webViewLink': drive_file['webViewLink']
    }

def remove_repeat_newlines(text):
    cleaned_text = re.sub(r'(\r\n|\n){2,}', '\n', text)
    return cleaned_text