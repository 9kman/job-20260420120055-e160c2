from datetime import datetime
from app import db
import uuid


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    subscription_tier = db.Column(db.String(50), default='free')
    subscription_status = db.Column(db.String(50), default='active')
    subscription_end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    email_accounts = db.relationship('EmailAccount', backref='user', lazy='dynamic')
    ai_requests = db.relationship('AIRequest', backref='user', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'subscription_tier': self.subscription_tier,
            'subscription_status': self.subscription_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    tier = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='active')
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    stripe_subscription_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tier': self.tier,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None
        }


class EmailAccount(db.Model):
    __tablename__ = 'email_accounts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    email_address = db.Column(db.String(255), nullable=False)
    provider = db.Column(db.String(50), nullable=False)
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    token_expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = db.relationship('EmailMessage', backref='email_account', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'email_address': self.email_address,
            'provider': self.provider,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class EmailMessage(db.Model):
    __tablename__ = 'email_messages'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email_account_id = db.Column(db.String(36), db.ForeignKey('email_accounts.id'), nullable=False)
    message_id = db.Column(db.String(255))
    subject = db.Column(db.String(500))
    sender = db.Column(db.String(255))
    recipient = db.Column(db.String(255))
    body_text = db.Column(db.Text)
    body_html = db.Column(db.Text)
    received_at = db.Column(db.DateTime)
    is_read = db.Column(db.Boolean, default=False)
    labels = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'sender': self.sender,
            'recipient': self.recipient,
            'body_text': self.body_text,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'is_read': self.is_read,
            'labels': self.labels
        }


class AIRequest(db.Model):
    __tablename__ = 'ai_requests'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    request_type = db.Column(db.String(50), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    model_used = db.Column(db.String(100))
    tokens_used = db.Column(db.Integer)
    status = db.Column(db.String(50), default='pending')
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'request_type': self.request_type,
            'prompt': self.prompt,
            'response': self.response,
            'model_used': self.model_used,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DailyUsage(db.Model):
    __tablename__ = 'daily_usage'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    emails_sent = db.Column(db.Integer, default=0)
    ai_requests_made = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='unique_user_date'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'emails_sent': self.emails_sent,
            'ai_requests_made': self.ai_requests_made
        }