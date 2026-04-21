# AI SaaS MVP - Claude API + Gmail + Outlook + SMTP Integration

A production-ready AI SaaS subscription platform integrating Claude API with Gmail, Outlook, and SMTP email services.

## Features

- **AI-Powered Email Composition**: Use Claude API to generate professional emails
- **Email Summarization**: Quickly summarize long email threads
- **Smart Responses**: Generate contextually appropriate email responses
- **Multi-Provider Support**: Connect Gmail and Outlook accounts
- **SMTP Integration**: Send emails via SMTP
- **Subscription Tiers**: Free, Pro, and Enterprise tiers with different usage limits
- **Usage Tracking**: Daily limits on AI requests and emails sent

## Tech Stack

- **Backend**: Flask 3.0 with SQLAlchemy ORM
- **AI**: Anthropic Claude API
- **Email**: Gmail API, Outlook API, SMTP
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis
- **Frontend**: HTML5/CSS3/JavaScript
- **Container**: Docker & Docker Compose

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Environment Variables

Create a `.env` file with the following:

```env
FLASK_ENV=development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_saas_mvp
REDIS_URL=redis://localhost:6379/0

ANTHROPIC_API_KEY=your_anthropic_api_key
CLAUDE_MODEL=claude-3-sonnet-20240229

GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GMAIL_REDIRECT_URI=http://localhost:5000/api/auth/gmail/callback

OUTLOOK_CLIENT_ID=your_outlook_client_id
OUTLOOK_CLIENT_SECRET=your_outlook_client_secret
OUTLOOK_REDIRECT_URI=http://localhost:5000/api/auth/outlook/callback

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```bash
   flask db upgrade
   ```

4. Run the application:
   ```bash
   python run.py
   ```

### Using Docker

```bash
docker-compose up -d
```

## API Endpoints

### Health
- `GET /api/health` - Health check

### Users
- `POST /api/users` - Create user
- `GET /api/users/<user_id>` - Get user
- `POST /api/users/<user_id>/subscription` - Update subscription

### Email Accounts
- `POST /api/email-accounts` - Add email account
- `GET /api/users/<user_id>/email-accounts` - Get user's accounts
- `GET /api/email-accounts/<account_id>/messages` - Get messages

### AI
- `POST /api/ai/compose` - AI compose email
- `POST /api/ai/summarize` - AI summarize content
- `GET /api/ai/requests/<request_id>` - Get AI request status

### Email
- `POST /api/email/send` - Send email via SMTP

### Usage
- `GET /api/users/<user_id>/usage` - Get usage stats
- `GET /api/users/<user_id>/usage/today` - Get today's usage

### Authentication
- `GET /api/auth/gmail/init` - Initialize Gmail OAuth
- `GET /api/auth/gmail/callback` - Gmail OAuth callback
- `GET /api/auth/outlook/init` - Initialize Outlook OAuth
- `GET /api/auth/outlook/callback` - Outlook OAuth callback

## Subscription Tiers

| Tier | AI Requests/Day | Emails/Day |
|------|-----------------|------------|
| Free | 50 | 10 |
| Pro | 500 | 100 |
| Enterprise | Unlimited | Unlimited |

## Testing

```bash
pytest tests/
```

## Project Structure

```
project/
├── app/
│   ├── api/           # API routes
│   ├── models/        # Database models
│   ├── services/     # External services (Claude, Gmail, Outlook, SMTP)
│   ├── utils/        # Utility functions
│   ├── config.py     # Configuration
│   └── __init__.py   # App factory
├── frontend/         # Frontend assets
├── migrations/       # Database migrations
├── tests/           # Test files
├── requirements.txt  # Python dependencies
├── Dockerfile       # Docker configuration
├── docker-compose.yml
└── run.py           # Application entry point
```

## License

MIT