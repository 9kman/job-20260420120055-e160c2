# SPEC.md — AI SaaS MVP: Claude API + Email Integration

## 1. Project Overview

**Project:** AI SaaS MVP — Claude API + Gmail + Outlook + SMTP Integration Platform
**Job ID:** JOB-20260420120055-e160c2
**Tier:** MICRO
**Stack:** Flask 3.0 + Anthropic Claude API + Gmail/Outlook OAuth + SMTP + PostgreSQL + Celery/Redis + Docker
**Repository:** https://github.com/9KMan/JOB-20260420120055-e160c2

Production-ready AI SaaS subscription platform enabling users to compose emails with Claude, summarize threads, generate smart responses — connected to Gmail, Outlook, and SMTP providers.

---

## 2. Tech Stack

| Layer           | Technology                                        |
|----------------|--------------------------------------------------|
| Backend         | Flask 3.0, Flask-SQLAlchemy, Flask-Migrate      |
| AI              | Anthropic Claude API (claude_service)            |
| Email           | Gmail API (google-api-python-client), Outlook (msal), SMTP |
| Database        | PostgreSQL                                       |
| Task Queue      | Celery 5.3 + Redis 5                            |
| Migrations      | Alembic                                          |
| Frontend        | Single HTML (18KB) — gradient SaaS landing page  |
| Container       | Docker + Docker Compose                           |
| Testing         | pytest + conftest                                |

---

## 3. Data Models

### User
| Column               | Type         | Notes                    |
|---------------------|--------------|-------------------------|
| id                  | String(36)  | PK (UUID string)         |
| email               | String(255)  | UNIQUE, NOT NULL        |
| password_hash       | String(255)  | NOT NULL                 |
| full_name           | String(255)  | nullable                 |
| subscription_tier   | String(50)   | DEFAULT 'free'           |
| gmail_connected     | Boolean      | DEFAULT False            |
| outlook_connected   | Boolean      | DEFAULT False            |
| created_at          | DateTime     | DEFAULT utcnow           |
| updated_at          | DateTime     | AUTO on update           |

### EmailMessage
| Column         | Type         | Notes                    |
|---------------|--------------|-------------------------|
| id            | String(36)   | PK                       |
| user_id       | String(36)   | FK → users.id           |
| provider      | String(20)   | 'gmail'/'outlook'/'smtp'|
| subject       | String(500)  | nullable                 |
| body          | Text         | nullable                 |
| sender        | String(255)  | NOT NULL                 |
| recipient     | String(255)  | NOT NULL                 |
| sent_at       | DateTime     | nullable                 |
| created_at    | DateTime     | DEFAULT utcnow           |

---

## 4. Services

### ClaudeService (app/services/claude_service.py)
- `compose_email(context, recipient_name, tone)` → generates professional email via Claude API
- `summarize_email_thread(emails)` → summarizes email thread
- `generate_response(incoming_email, tone)` → generates AI reply to incoming email
- Uses `ANTHROPIC_API_KEY` from config

### GmailService (app/services/gmail_service.py)
- OAuth2 credentials via `create_credentials(token, refresh_token, token_uri)`
- `get_messages(max_results=50)` → list Gmail messages
- `get_message(msg_id)` → fetch single message
- `send_email(to, subject, body, is_html)` → send via Gmail API
- `mark_as_read(msg_id)`, `mark_as_unread(msg_id)`
- Scopes: `gmail.modify`, `gmail.send`

### OutlookService (app/services/outlook_service.py)
- MSAL authentication
- `get_messages(max_results=50)` → list Outlook messages
- `get_message(msg_id)` → fetch single message
- `send_email(to, subject, body, is_html)` → send via Outlook

### SMTPService (app/services/smtp_service.py)
- `connect()` / `disconnect()` with context manager
- `send_email(from, to, subject, body, is_html)` → send via SMTP
- `send_bulk_emails(...)` → bulk send
- Supports TLS

---

## 5. Configuration

Environment variables (`.env`):
```
FLASK_ENV=production
DATABASE_URL=postgresql://postgres:<password>@db:5432/ai_saas_mvp
REDIS_URL=redis://redis:6379/0
ANTHROPIC_API_KEY=<key>
GMAIL_CLIENT_ID=<id>
GMAIL_CLIENT_SECRET=<secret>
OUTLOOK_CLIENT_ID=<id>
OUTLOOK_CLIENT_SECRET=<secret>
SMTP_HOST=<host>
SMTP_PORT=<port>
SMTP_USERNAME=<user>
SMTP_PASSWORD=<pass>
```

Config classes: `DevelopmentConfig`, `ProductionConfig`, `TestingConfig`

---

## 6. Docker

Services: `app` (Flask + Celery worker) + `db` (PostgreSQL) + `redis` (Redis)

```yaml
app:
  build: .
  ports: ["5000:5000"]
  environment: [FLASK_ENV, DATABASE_URL, REDIS_URL, ANTHROPIC_API_KEY, ...]
  depends_on: [db, redis]
db:
  image: postgres:15-alpine
redis:
  image: redis:7-alpine
```

---

## 7. File Structure

```
JOB-20260420120055-e160c2/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt     # Flask, FastAPI, Celery, Anthropic, Google API, MSAL, etc.
├── run.py               # app.run() entry point
├── README.md
│
├── app/
│   ├── __init__.py     # create_app(), db/migrate/CORS init, celery config
│   ├── config.py       # Development/Production/Testing configs
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py   # User, EmailMessage SQLAlchemy models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── claude_service.py   # Anthropic Claude API
│   │   ├── gmail_service.py   # Gmail API (google-api-python-client)
│   │   ├── outlook_service.py  # Outlook (msal + outlook client)
│   │   └── smtp_service.py    # SMTP
│   └── utils/
│       └── __init__.py
│
├── frontend/
│   └── index.html      # 18KB SaaS landing page (gradient, tiers, pricing)
│
├── migrations/
│   └── 001_initial.py  # Alembic migration: users + email_messages tables
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_api.py
```

---

## 8. Quality

- pytest with conftest fixtures
- Alembic migrations for schema management
- No hardcoded secrets — all from environment variables
- Multi-provider email abstraction (Gmail/Outlook/SMTP)
- Celery task queue for async email operations
- Redis for Celery broker and caching
