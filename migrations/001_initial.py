"""Initial migration

Revision ID: 001
Revises:
Create Date: 2026-04-21

"""
from alembic import op
import sqlalchemy as sa


revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('subscription_tier', sa.String(50), default='free'),
        sa.Column('subscription_status', sa.String(50), default='active'),
        sa.Column('subscription_end_date', sa.DateTime),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime)
    )

    op.create_table(
        'subscriptions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('tier', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('start_date', sa.DateTime),
        sa.Column('end_date', sa.DateTime),
        sa.Column('stripe_subscription_id', sa.String(255)),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime)
    )

    op.create_table(
        'email_accounts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('email_address', sa.String(255), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('access_token', sa.Text),
        sa.Column('refresh_token', sa.Text),
        sa.Column('token_expires_at', sa.DateTime),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime)
    )

    op.create_table(
        'email_messages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email_account_id', sa.String(36), sa.ForeignKey('email_accounts.id'), nullable=False),
        sa.Column('message_id', sa.String(255)),
        sa.Column('subject', sa.String(500)),
        sa.Column('sender', sa.String(255)),
        sa.Column('recipient', sa.String(255)),
        sa.Column('body_text', sa.Text),
        sa.Column('body_html', sa.Text),
        sa.Column('received_at', sa.DateTime),
        sa.Column('is_read', sa.Boolean, default=False),
        sa.Column('labels', sa.String(255)),
        sa.Column('created_at', sa.DateTime)
    )

    op.create_table(
        'ai_requests',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('request_type', sa.String(50), nullable=False),
        sa.Column('prompt', sa.Text, nullable=False),
        sa.Column('response', sa.Text),
        sa.Column('model_used', sa.String(100)),
        sa.Column('tokens_used', sa.Integer),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('error_message', sa.Text),
        sa.Column('created_at', sa.DateTime),
        sa.Column('completed_at', sa.DateTime)
    )

    op.create_table(
        'daily_usage',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('emails_sent', sa.Integer, default=0),
        sa.Column('ai_requests_made', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.UniqueConstraint('user_id', 'date', name='unique_user_date')
    )


def downgrade():
    op.drop_table('daily_usage')
    op.drop_table('ai_requests')
    op.drop_table('email_messages')
    op.drop_table('email_accounts')
    op.drop_table('subscriptions')
    op.drop_table('users')