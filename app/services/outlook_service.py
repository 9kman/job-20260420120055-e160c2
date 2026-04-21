from outlook import OutlookClient
from app.config import Config
import msal


class OutlookService:
    def __init__(self, credentials=None):
        self.creds = credentials
        self.client = None
        if self.creds:
            self._build_client()

    def _build_client(self):
        if self.creds:
            self.client = OutlookClient(creds=self.creds)

    @staticmethod
    def create_credentials(token, refresh_token, token_uri):
        return {
            'token': token,
            'refresh_token': refresh_token,
            'token_uri': token_uri,
            'client_id': Config.OUTLOOK_CLIENT_ID,
            'client_secret': Config.OUTLOOK_CLIENT_SECRET
        }

    def get_messages(self, max_results=50):
        if not self.client:
            return {'error': 'Outlook service not authenticated'}

        try:
            messages = self.client.mailbox.get_messages(top=max_results)
            return {'messages': [self._parse_message(msg) for msg in messages]}
        except Exception as e:
            return {'error': str(e)}

    def get_message(self, msg_id):
        if not self.client:
            return {'error': 'Outlook service not authenticated'}

        try:
            message = self.client.mailbox.get_message(msg_id)
            return self._parse_message(message)
        except Exception as e:
            return {'error': str(e)}

    def _parse_message(self, message):
        return {
            'message_id': getattr(message, 'id', ''),
            'subject': getattr(message, 'subject', ''),
            'sender': str(getattr(message, 'from', '')),
            'recipient': str(getattr(message, 'to_recipients', '')),
            'date': str(getattr(message, 'received_date_time', '')),
            'body': getattr(message, 'body', ''),
            'is_read': getattr(message, 'is_read', True)
        }

    def send_email(self, to, subject, body, is_html=False):
        if not self.client:
            return {'error': 'Outlook service not authenticated'}

        try:
            message = {
                'subject': subject,
                'body': {'contentType': 'HTML' if is_html else 'Text', 'content': body},
                'toRecipients': [{'emailAddress': {'address': to}}]
            }

            sent_message = self.client.mailbox.send_message(message)
            return {
                'message_id': sent_message.id,
                'status': 'sent'
            }
        except Exception as e:
            return {'error': str(e)}


outlook_service = OutlookService()