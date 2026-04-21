from google.oauth2.credentials import Credentials
from google_auth_httplib2 import AuthorizedSession
from googleapiclient.discovery import build
from app.config import Config
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class GmailService:
    def __init__(self, credentials=None):
        self.creds = credentials
        self.service = None
        if self.creds:
            self._build_service()

    def _build_service(self):
        if self.creds:
            self.service = build('gmail', 'v1', credentials=self.creds)

    @staticmethod
    def create_credentials(token, refresh_token, token_uri):
        return Credentials(
            token=token,
            refresh_token=refresh_token,
            token_uri=token_uri,
            client_id=Config.GMAIL_CLIENT_ID,
            client_secret=Config.GMAIL_CLIENT_SECRET,
            scopes=['https://www.googleapis.com/auth/gmail.modify',
                    'https://www.googleapis.com/auth/gmail.send']
        )

    def get_messages(self, max_results=50):
        if not self.service:
            return {'error': 'Gmail service not authenticated'}

        try:
            messages = self.service.users().messages().list(
                userId='me',
                maxResults=max_results
            ).execute()

            message_list = []
            for msg_id in messages.get('messages', []):
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg_id['id'],
                    format='full'
                ).execute()
                message_list.append(self._parse_message(message))

            return {'messages': message_list}
        except Exception as e:
            return {'error': str(e)}

    def get_message(self, msg_id):
        if not self.service:
            return {'error': 'Gmail service not authenticated'}

        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            return self._parse_message(message)
        except Exception as e:
            return {'error': str(e)}

    def _parse_message(self, message):
        headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}

        body = ''
        html_body = ''
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part.get('body', {}):
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html' and 'data' in part.get('body', {}):
                    html_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')

        return {
            'message_id': message['id'],
            'thread_id': message['threadId'],
            'subject': headers.get('Subject', ''),
            'sender': headers.get('From', ''),
            'recipient': headers.get('To', ''),
            'date': headers.get('Date', ''),
            'body': body,
            'html_body': html_body,
            'labels': message.get('labelIds', []),
            'is_read': 'UNREAD' not in message.get('labelIds', [])
        }

    def send_email(self, to, subject, body, is_html=False):
        if not self.service:
            return {'error': 'Gmail service not authenticated'}

        try:
            message = MIMEMultipart('alternative')
            message['to'] = to
            message['subject'] = subject

            if is_html:
                message.attach(MIMEText(body, 'html'))
            else:
                message.attach(MIMEText(body, 'plain'))

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': encoded_message}
            ).execute()

            return {
                'message_id': sent_message['id'],
                'status': 'sent'
            }
        except Exception as e:
            return {'error': str(e)}

    def mark_as_read(self, msg_id):
        if not self.service:
            return {'error': 'Gmail service not authenticated'}

        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return {'status': 'success'}
        except Exception as e:
            return {'error': str(e)}

    def mark_as_unread(self, msg_id):
        if not self.service:
            return {'error': 'Gmail service not authenticated'}

        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            return {'status': 'success'}
        except Exception as e:
            return {'error': str(e)}


gmail_service = GmailService()