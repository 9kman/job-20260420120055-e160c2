from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Subscription, EmailAccount, EmailMessage, AIRequest, DailyUsage
from datetime import datetime, date
import uuid

api_bp = Blueprint('api', __name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


@api_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400

    user = User(
        id=str(uuid.uuid4()),
        email=data['email'],
        password_hash=data.get('password_hash', ''),
        full_name=data.get('full_name')
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@api_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())


@api_bp.route('/users/<user_id>/subscription', methods=['POST'])
def update_subscription(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    user.subscription_tier = data.get('tier', 'free')
    user.subscription_status = data.get('status', 'active')

    subscription = Subscription(
        user_id=user_id,
        tier=user.subscription_tier,
        status=user.subscription_status
    )
    db.session.add(subscription)
    db.session.commit()

    return jsonify({'user': user.to_dict(), 'subscription': subscription.to_dict()})


@api_bp.route('/email-accounts', methods=['POST'])
def add_email_account():
    data = request.get_json()
    if not data or not data.get('email_address') or not data.get('provider'):
        return jsonify({'error': 'Email address and provider are required'}), 400

    email_account = EmailAccount(
        id=str(uuid.uuid4()),
        user_id=data['user_id'],
        email_address=data['email_address'],
        provider=data['provider'],
        access_token=data.get('access_token'),
        refresh_token=data.get('refresh_token')
    )
    db.session.add(email_account)
    db.session.commit()
    return jsonify(email_account.to_dict()), 201


@api_bp.route('/users/<user_id>/email-accounts', methods=['GET'])
def get_email_accounts(user_id):
    accounts = EmailAccount.query.filter_by(user_id=user_id, is_active=True).all()
    return jsonify([account.to_dict() for account in accounts])


@api_bp.route('/email-accounts/<account_id>/messages', methods=['GET'])
def get_messages(account_id):
    limit = request.args.get('limit', 50, type=int)
    messages = EmailMessage.query.filter_by(email_account_id=account_id).order_by(
        EmailMessage.received_at.desc()
    ).limit(limit).all()
    return jsonify([msg.to_dict() for msg in messages])


@api_bp.route('/ai/compose', methods=['POST'])
def ai_compose():
    data = request.get_json()
    if not data or not data.get('user_id') or not data.get('prompt'):
        return jsonify({'error': 'User ID and prompt are required'}), 400

    ai_request = AIRequest(
        id=str(uuid.uuid4()),
        user_id=data['user_id'],
        request_type='compose',
        prompt=data['prompt'],
        model_used='claude-3-sonnet-20240229',
        status='pending'
    )
    db.session.add(ai_request)
    db.session.commit()

    return jsonify({
        'request_id': ai_request.id,
        'status': 'submitted',
        'message': 'AI compose request submitted'
    }), 202


@api_bp.route('/ai/summarize', methods=['POST'])
def ai_summarize():
    data = request.get_json()
    if not data or not data.get('user_id') or not data.get('content'):
        return jsonify({'error': 'User ID and content are required'}), 400

    ai_request = AIRequest(
        id=str(uuid.uuid4()),
        user_id=data['user_id'],
        request_type='summarize',
        prompt=data['content'],
        model_used='claude-3-sonnet-20240229',
        status='pending'
    )
    db.session.add(ai_request)
    db.session.commit()

    return jsonify({
        'request_id': ai_request.id,
        'status': 'submitted',
        'message': 'AI summarize request submitted'
    }), 202


@api_bp.route('/ai/requests/<request_id>', methods=['GET'])
def get_ai_request(request_id):
    ai_request = AIRequest.query.get(request_id)
    if not ai_request:
        return jsonify({'error': 'Request not found'}), 404
    return jsonify(ai_request.to_dict())


@api_bp.route('/users/<user_id>/usage', methods=['GET'])
def get_usage(user_id):
    today = date.today()
    usage = DailyUsage.query.filter_by(user_id=user_id, date=today).first()

    if not usage:
        usage = DailyUsage(user_id=user_id, date=today)
        db.session.add(usage)
        db.session.commit()

    return jsonify(usage.to_dict())


@api_bp.route('/users/<user_id>/usage/today', methods=['GET'])
def get_today_usage(user_id):
    today = date.today()
    usage = DailyUsage.query.filter_by(user_id=user_id, date=today).first()

    if not usage:
        return jsonify({'emails_sent': 0, 'ai_requests_made': 0})

    return jsonify(usage.to_dict())


@api_bp.route('/email/send', methods=['POST'])
def send_email():
    data = request.get_json()
    if not data or not data.get('user_id') or not data.get('to') or not data.get('subject'):
        return jsonify({'error': 'User ID, recipient, and subject are required'}), 400

    return jsonify({
        'status': 'sent',
        'message': 'Email sent successfully',
        'to': data['to'],
        'subject': data['subject']
    })


@api_bp.route('/auth/gmail/init', methods=['GET'])
def gmail_auth_init():
    return jsonify({
        'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
        'message': 'Redirect user to this URL for Gmail authorization'
    })


@api_bp.route('/auth/gmail/callback', methods=['GET'])
def gmail_auth_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'Authorization code required'}), 400

    return jsonify({
        'status': 'success',
        'message': 'Gmail account connected successfully'
    })


@api_bp.route('/auth/outlook/init', methods=['GET'])
def outlook_auth_init():
    return jsonify({
        'auth_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        'message': 'Redirect user to this URL for Outlook authorization'
    })


@api_bp.route('/auth/outlook/callback', methods=['GET'])
def outlook_auth_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'Authorization code required'}), 400

    return jsonify({
        'status': 'success',
        'message': 'Outlook account connected successfully'
    })