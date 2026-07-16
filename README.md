# Issue Tracker

Multiple organizations share one app, and
each organization only ever sees its own issues.

![Tests](https://img.shields.io/badge/tests-20%2F20%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-black)
![Docker](https://img.shields.io/badge/docker-ready-2496ed)
![License](https://img.shields.io/badge/license-MIT-blue)

## Screenshots

| Login | Dashboard |
|---|---|
| ![login](assets/screen-login.png) | ![dashboard](assets/screen-dashboard.png) |

## Notes

I built this to practice writing a backend in layers instead of one big file.
A few things I focused on:

- Tenant isolation is done in the base repository, which filters every query by
  `tenant_id`. So it's enforced in one place, not repeated in every route. The
  test `test_issue_isolation_between_tenants` checks it holds.
- Routes are thin. Business rules go in `services/`, database access in
  `repositories/`, request/response shapes in `schemas/`.
- Passwords are hashed, roles are admin/member, forms have CSRF protection, and
  login and writes are rate-limited.
- `docker compose up` runs the app with Postgres. Alembic handles the schema and
  `/health` backs the container health check.

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

pip install -r requirements.txt
python app.py
```

### Run with Docker (app + PostgreSQL)

```bash
docker compose up --build          
docker compose exec web flask db upgrade
```

### Database migrations (Alembic / Flask-Migrate)

```bash
export USE_MIGRATIONS=1            
flask db upgrade                  
flask db migrate -m "your change"  
```
## Project Structure

```
issue-tracker/
├── app.py                  
├── models.py               
├── config.py                
│
├── services/              
│   ├── auth_service.py      
│   ├── permission_service.py 
│   ├── issue_service.py      
│   ├── comment_service.py    
│   └── email_service.py      
│
├── repositories/             
│   ├── base_repository.py
│   ├── issue_repository.py
│   └── tenant_repository.py
│
├── schemas/                  
│   ├── base_schema.py
│   ├── issue_schema.py
│   └── comment_schema.py
│
├── exceptions/               
│   └── custom_exceptions.py
│
├── migrations/               
├── templates/               
├── static/                  
├── tests/                    
│
├── Dockerfile                
├── docker-compose.yml        
├── requirements.txt
└── .env
```

## Configuration

```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///issue_tracker.db
FLASK_ENV=development
```

For PostgreSQL production:
```
DATABASE_URL=postgresql://user:password@localhost/issue_tracker
```

## What it does

Register an org, log in, and create / assign / comment on issues that only your
org can see. Roles are admin and member. There's a JSON API next to the web UI,
the auth and API routes are rate-limited, it sends an email when an issue changes,
and there's a dark-mode toggle.

## Rate limits

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
pytest -v

pytest tests/test_auth.py -v

pytest tests/test_auth.py::TestLogin::test_login_success -v
```

20 tests: auth, issue CRUD, cross-tenant isolation, comments, CSRF, and the health check.

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

## License

MIT. See the LICENSE file.
