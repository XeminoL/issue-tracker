# Issue Tracker

Multi-tenant issue tracking system with clean architecture, automatic tenant isolation, and rate limiting.

![Tests](https://img.shields.io/badge/tests-15%2F15-brightgreen)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

## Purpose

Track issues across multiple tenants with complete data isolation, role-based access, email notifications, and API rate limiting.

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

## Project Structure

```
issue-tracker/
├── app.py                    # Routes & error handlers
├── models.py                 # Database models
├── config.py                 # Configuration
├── email_service.py          # Email notifications
├── conftest.py               # Test fixtures
│
├── services/                 # Business logic
│   ├── auth_service.py       # Password hashing
│   ├── permission_service.py # Authorization
│   ├── issue_service.py      # Issue workflows
│   └── comment_service.py    # Comment workflows
│
├── repositories/             # Data access (auto tenant filter)
│   ├── base_repository.py
│   ├── issue_repository.py
│   └── tenant_repository.py
│
├── schemas/                  # Input validation & serialization
│   ├── issue_schema.py
│   └── comment_schema.py
│
├── exceptions/               # Custom exceptions
│   └── custom_exceptions.py
│
├── templates/                # HTML templates
├── static/                   # CSS, JS
├── tests/                    # Test suite
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

All tests pass: **15/15 ✅**

## Dependencies

- Flask 2.3.3
- Flask-SQLAlchemy 3.0.5
- Flask-Limiter 4.1.1
- SQLAlchemy 2.0.50
- Werkzeug 2.3.7
- PyJWT 2.9.0
- python-dotenv 1.0.0
- pytest 7.4.0
- pytest-flask 1.2.0

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
