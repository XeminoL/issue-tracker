# Issue Tracker

A multi-tenant issue-tracking backend built in Flask with **clean, layered architecture**,
automatic tenant isolation, role-based access control, CSRF protection, rate limiting,
database migrations, and Docker.

![Tests](https://img.shields.io/badge/tests-20%2F20%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-black)
![Docker](https://img.shields.io/badge/docker-ready-2496ed)
![License](https://img.shields.io/badge/license-MIT-blue)

Track issues across multiple organizations (tenants) with complete data isolation between
them, role-based access, email notifications, and per-endpoint rate limiting.

## Why this project

It is a small app built the way a real backend is built — not a single-file demo. The point
was to practice **separation of concerns** and **security-by-default multi-tenancy**:

- **Layered architecture** — routes stay thin; business rules live in services; all database
  access goes through repositories; every payload passes through a schema. Each layer has one
  job, so the code is easy to test and change.
- **Tenant isolation by construction** — the base repository filters every query by the current
  tenant automatically, so one organization can never read another's data by accident. There is
  a test (`test_issue_isolation_between_tenants`) that proves it.
- **Defence in depth** — hashed passwords, role checks (admin/member), input validation,
  CSRF protection on the HTML forms, and rate limits on the auth and API endpoints.
- **Ready to run anywhere** — `docker compose up` brings up the app with PostgreSQL; Alembic
  migrations own the schema; a `/health` endpoint backs the container health check.

## Architecture at a glance

```
        HTTP request
            │
     ┌──────▼───────┐   thin controllers: parse, delegate, respond
     │   app.py     │   (routes + error handlers)
     └──────┬───────┘
            │
     ┌──────▼───────┐   business rules & authorization
     │  services/   │   auth · permission · issue · comment
     └──────┬───────┘
            │
     ┌──────▼───────┐   data access — auto-filters by tenant
     │ repositories/│   base · issue · tenant
     └──────┬───────┘
            │
     ┌──────▼───────┐   SQLAlchemy models  →  SQLite / PostgreSQL
     │  models.py   │   Tenant · User · Issue · Comment
     └──────────────┘

  schemas/     validate input & serialize output (marshmallow-style)
  exceptions/  typed domain errors, mapped to HTTP status codes
```

Data model: **Tenant → Users → Issues → Comments**, with every table scoped to a tenant.

## Quick Start

```bash
git clone https://github.com/XeminoL/issue-tracker.git
cd issue-tracker

python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1
# macOS/Linux: source venv/bin/activate

pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

### Run with Docker (app + PostgreSQL)

```bash
docker compose up --build          # starts the app and a Postgres database
docker compose exec web flask db upgrade   # apply migrations
# Open http://localhost:5000  ·  health check at /health
```

### Database migrations (Alembic / Flask-Migrate)

```bash
export USE_MIGRATIONS=1            # let Alembic own the schema (skip create_all)
flask db upgrade                   # apply the latest migration
flask db migrate -m "your change"  # after editing models, generate a new one
```

## Project Structure

```
issue-tracker/
├── app.py                    # Routes, error handlers, CSRF, /health
├── models.py                 # Database models (Tenant · User · Issue · Comment)
├── config.py                 # Configuration (env-driven)
│
├── services/                 # Business logic
│   ├── auth_service.py       # Password hashing
│   ├── permission_service.py # Authorization
│   ├── issue_service.py      # Issue workflows
│   ├── comment_service.py    # Comment workflows
│   └── email_service.py      # Email notifications
│
├── repositories/             # Data access (auto tenant filter)
│   ├── base_repository.py
│   ├── issue_repository.py
│   └── tenant_repository.py
│
├── schemas/                  # Input validation & serialization
│   ├── base_schema.py
│   ├── issue_schema.py
│   └── comment_schema.py
│
├── exceptions/               # Typed domain errors → HTTP codes
│   └── custom_exceptions.py
│
├── migrations/               # Alembic migrations (Flask-Migrate)
├── templates/                # HTML templates (CSRF-protected forms)
├── static/                   # CSS, JS
├── tests/                    # Test suite — conftest.py + 3 test files
│
├── Dockerfile                # Production image (gunicorn)
├── docker-compose.yml        # App + PostgreSQL
├── requirements.txt
└── .env
```

## Configuration

```bash
# .env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///issue_tracker.db
FLASK_ENV=development
```

For PostgreSQL production:
```
DATABASE_URL=postgresql://user:password@localhost/issue_tracker
```

## Features

- Multi-tenant with automatic data isolation
- User registration and authentication
- Issue CRUD with status tracking
- Comments on issues
- Email notifications
- Role-based access (admin/member)
- API rate limiting
- Dark mode
- RESTful API

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `POST /login` | 5/minute |
| `POST /register` | 3/minute |
| `GET /api/issues` | 30/minute |
| `POST /api/issues` | 10/minute |
| `PUT /api/issues/<id>` | 10/minute |
| `DELETE /api/issues/<id>` | 5/minute |
| Default | 200/day, 50/hour |

## API

### Register
```http
POST /register
Content-Type: application/x-www-form-urlencoded

tenant_name=Company&tenant_slug=company&name=John&email=john@example.com&password=pass123
```

### Login
```http
POST /login
tenant_slug=company&email=john@example.com&password=pass123
```

### Get Issues
```http
GET /api/issues
```

### Create Issue
```http
POST /api/issues
Content-Type: application/json

{"title": "Bug title", "description": "Bug description"}
```

### Update Issue
```http
PUT /api/issues/{issue_id}
Content-Type: application/json

{"title": "New title", "status": "closed"}
```

### Delete Issue
```http
DELETE /api/issues/{issue_id}
```

### Assign Issue
```http
POST /api/issues/{issue_id}/assign
Content-Type: application/json

{"assigned_to": 2}
```

### Get Comments
```http
GET /api/issues/{issue_id}/comments
```

### Create Comment
```http
POST /api/issues/{issue_id}/comments
Content-Type: application/json

{"content": "Comment text"}
```

## Testing

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_auth.py -v

# Run single test
pytest tests/test_auth.py::TestLogin::test_login_success -v
```

All tests pass: **20/20 ✅** — 8 auth tests, 7 issue tests (CRUD, missing-auth, cross-tenant
isolation), 2 comment tests, 2 CSRF tests (form rejected without a token; API exempt), and a
health-check test.

## Dependencies

- Flask 2.3.3
- Flask-SQLAlchemy 3.0.5
- Flask-Limiter 4.1.1
- Flask-WTF 1.2.1 (CSRF protection)
- Flask-Migrate 4.0.5 (Alembic migrations)
- SQLAlchemy 2.0.50
- Werkzeug 2.3.7
- psycopg2-binary 2.9.9 (PostgreSQL driver)
- gunicorn 21.2.0 (production server)
- python-dotenv 1.0.0
- pytest 7.4.0 · pytest-flask 1.2.0

## Development

To add a feature:

1. Update database model if needed (models.py)
2. Add repository methods (repositories/)
3. Add service logic (services/)
4. Add validation (schemas/)
5. Add route handler (app.py)
6. Add tests (tests/)
7. Run `pytest -v` to verify

## License

MIT - See LICENSE file
