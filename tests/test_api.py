import pytest
from app import create_app, db
from app.models import User, Subscription, EmailAccount, AIRequest


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data


class TestUserEndpoints:
    def test_create_user(self, client):
        response = client.post('/api/users', json={
            'email': 'test@example.com',
            'password_hash': 'hashed_password',
            'full_name': 'Test User'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['email'] == 'test@example.com'
        assert data['full_name'] == 'Test User'
        assert 'id' in data

    def test_get_user(self, client):
        create_response = client.post('/api/users', json={
            'email': 'test@example.com',
            'full_name': 'Test User'
        })
        user_id = create_response.get_json()['id']

        response = client.get(f'/api/users/{user_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['email'] == 'test@example.com'

    def test_get_nonexistent_user(self, client):
        response = client.get('/api/users/nonexistent-id')
        assert response.status_code == 404


class TestSubscriptionEndpoints:
    def test_update_subscription(self, client):
        create_response = client.post('/api/users', json={
            'email': 'test@example.com',
            'full_name': 'Test User'
        })
        user_id = create_response.get_json()['id']

        response = client.post(f'/api/users/{user_id}/subscription', json={
            'tier': 'pro',
            'status': 'active'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['subscription_tier'] == 'pro'
        assert data['subscription']['tier'] == 'pro'


class TestEmailAccountEndpoints:
    def test_add_email_account(self, client):
        create_response = client.post('/api/users', json={
            'email': 'test@example.com',
            'full_name': 'Test User'
        })
        user_id = create_response.get_json()['id']

        response = client.post('/api/email-accounts', json={
            'user_id': user_id,
            'email_address': 'test@gmail.com',
            'provider': 'gmail'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['email_address'] == 'test@gmail.com'
        assert data['provider'] == 'gmail'

    def test_get_user_email_accounts(self, client):
        create_response = client.post('/api/users', json={
            'email': 'test@example.com',
            'full_name': 'Test User'
        })
        user_id = create_response.get_json()['id']

        client.post('/api/email-accounts', json={
            'user_id': user_id,
            'email_address': 'test@gmail.com',
            'provider': 'gmail'
        })

        response = client.get(f'/api/users/{user_id}/email-accounts')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['email_address'] == 'test@gmail.com'


class TestAIEndpoints:
    def test_ai_compose_request(self, client):
        create_response = client.post('/api/users', json={
            'email': 'test@example.com',
            'full_name': 'Test User'
        })
        user_id = create_response.get_json()['id']

        response = client.post('/api/ai/compose', json={
            'user_id': user_id,
            'prompt': 'Write a professional email'
        })
        assert response.status_code == 202
        data = response.get_json()
        assert data['status'] == 'submitted'
        assert 'request_id' in data

    def test_ai_compose_missing_fields(self, client):
        response = client.post('/api/ai/compose', json={
            'user_id': 'some-id'
        })
        assert response.status_code == 400

    def test_ai_summarize_request(self, client):
        create_response = client.post('/api/users', json={
            'email': 'test@example.com',
            'full_name': 'Test User'
        })
        user_id = create_response.get_json()['id']

        response = client.post('/api/ai/summarize', json={
            'user_id': user_id,
            'content': 'This is a long email content to summarize'
        })
        assert response.status_code == 202
        data = response.get_json()
        assert data['status'] == 'submitted'


class TestUsageEndpoints:
    def test_get_usage_new_user(self, client):
        create_response = client.post('/api/users', json={
            'email': 'test@example.com',
            'full_name': 'Test User'
        })
        user_id = create_response.get_json()['id']

        response = client.get(f'/api/users/{user_id}/usage')
        assert response.status_code == 200
        data = response.get_json()
        assert data['emails_sent'] == 0
        assert data['ai_requests_made'] == 0


class TestSendEmailEndpoint:
    def test_send_email_missing_fields(self, client):
        response = client.post('/api/email/send', json={
            'user_id': 'some-id'
        })
        assert response.status_code == 400

    def test_send_email_success(self, client):
        create_response = client.post('/api/users', json={
            'email': 'test@example.com',
            'full_name': 'Test User'
        })
        user_id = create_response.get_json()['id']

        response = client.post('/api/email/send', json={
            'user_id': user_id,
            'to': 'recipient@example.com',
            'subject': 'Test Subject',
            'body': 'Test Body'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'sent'


class TestAuthEndpoints:
    def test_gmail_auth_init(self, client):
        response = client.get('/api/auth/gmail/init')
        assert response.status_code == 200
        data = response.get_json()
        assert 'auth_url' in data

    def test_outlook_auth_init(self, client):
        response = client.get('/api/auth/outlook/init')
        assert response.status_code == 200
        data = response.get_json()
        assert 'auth_url' in data

    def test_gmail_callback_missing_code(self, client):
        response = client.get('/api/auth/gmail/callback')
        assert response.status_code == 400