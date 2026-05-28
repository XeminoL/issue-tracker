import pytest
from app import app, db
from models import Tenant, User
from services import AuthService

auth_service = AuthService()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def tenant(client):
    tenant = Tenant(name='Test Company', slug='test-company')
    db.session.add(tenant)
    db.session.commit()
    return tenant


@pytest.fixture
def user(tenant):
    user = User(
        name='John Doe',
        email='john@test.com',
        password_hash=auth_service.hash_password('password123'),
        tenant_id=tenant.id
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def authenticated_client(client, user, tenant):
    with client.session_transaction() as sess:
        sess['user_id'] = user.id
        sess['tenant_id'] = tenant.id
    return client
