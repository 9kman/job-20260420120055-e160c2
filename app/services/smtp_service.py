import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import Config


class SMTPService:
    def __init__(self, host=None, port=None, username=None, password=None):
        self.host = host or Config.SMTP_HOST
        self.port = port or Config.SMTP_PORT
        self.username = username or Config.SMTP_USERNAME
        self.password = password or Config.SMTP_PASSWORD
        self.server = None

    def connect(self):
        try:
            self.server = smtplib.SMTP(self.host, self.port)
            self.server.starttls()
            self.server.login(self.username, self.password)
            return {'status': 'connected'}
        except Exception as e:
            return {'error': str(e)}

    def disconnect(self):
        if self.server:
            try:
                self.server.quit()
                return {'status': 'disconnected'}
            except Exception as e:
                return {'error': str(e)}

    def send_email(self, from_addr, to_addr, subject, body, is_html=False):
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = from_addr
            msg['To'] = to_addr
            msg['Subject'] = subject

            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            if not self.server:
                self.connect()

            self.server.sendmail(from_addr, [to_addr], msg.as_string())
            return {
                'status': 'sent',
                'from': from_addr,
                'to': to_addr,
                'subject': subject
            }
        except Exception as e:
            return {'error': str(e)}

    def send_bulk_emails(self, from_addr, recipients, subject, body, is_html=False):
        results = []
        for recipient in recipients:
            result = self.send_email(from_addr, recipient, subject, body, is_html)
            results.append({'to': recipient, 'result': result})
        return results

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


smtp_service = SMTPService()