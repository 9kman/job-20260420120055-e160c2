from datetime import datetime, date
from functools import wraps
from flask import jsonify


def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def format_datetime(dt):
    if dt:
        return dt.isoformat()
    return None


def format_date(d):
    if d:
        return d.isoformat()
    return None


def require_subscription_tier(tier):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.models import User
            user_id = kwargs.get('user_id')
            if not user_id:
                return jsonify({'error': 'User ID required'}), 400

            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404

            tier_hierarchy = {'free': 0, 'pro': 1, 'enterprise': 2}
            user_tier_level = tier_hierarchy.get(user.subscription_tier, 0)
            required_tier_level = tier_hierarchy.get(tier, 0)

            if user_tier_level < required_tier_level:
                return jsonify({
                    'error': f'This feature requires {tier} subscription or higher'
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def check_daily_limit(user_id, usage_type, limit):
    from app.models import DailyUsage
    today = date.today()
    usage = DailyUsage.query.filter_by(user_id=user_id, date=today).first()

    if not usage:
        return True

    current_usage = getattr(usage, f'{usage_type}_made' if usage_type == 'ai_requests' else f'{usage_type}_sent', 0)
    return current_usage < limit


def increment_usage(user_id, usage_type):
    from app import db
    from app.models import DailyUsage
    today = date.today()

    usage = DailyUsage.query.filter_by(user_id=user_id, date=today).first()
    if not usage:
        usage = DailyUsage(user_id=user_id, date=today)
        db.session.add(usage)

    if usage_type == 'ai_requests':
        usage.ai_requests_made += 1
    elif usage_type == 'emails':
        usage.emails_sent += 1

    db.session.commit()
    return usage