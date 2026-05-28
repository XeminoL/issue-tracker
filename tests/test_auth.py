import pytest
from models import User, Tenant


class TestRegistration:
    def test_register_new_user(self, client):
        response = client.post('/register', data={
            'name': 'Jane Doe',
            'email': 'jane@test.com',
            'password': 'securepass123',
            'tenant_name': 'Jane Company',
            'tenant_slug': 'jane-company'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Issue Tracker' in response.data

        tenant = Tenant.query.filter_by(slug='jane-company').first()
        assert tenant is not None
        assert tenant.name == 'Jane Company'

        user = User.query.filter_by(email='jane@test.com').first()
        assert user is not None
        assert user.name == 'Jane Doe'

    def test_register_duplicate_tenant_slug(self, client, tenant):
        response = client.post('/register', data={
            'name': 'Another User',
            'email': 'another@test.com',
            'password': 'password123',
            'tenant_name': 'Another Company',
            'tenant_slug': 'test-company'
        })

        assert response.status_code == 200
        assert b'Tenant already exists' in response.data

    def test_register_missing_fields(self, client):
        response = client.post('/register', data={
            'name': 'John Doe',
            'email': 'john@test.com'
        })

        assert response.status_code == 200
        assert b'All fields are required' in response.data


class TestLogin:
    def test_login_success(self, client, user, tenant):
        response = client.post('/login', data={
            'email': 'john@test.com',
            'password': 'password123',
            'tenant_slug': 'test-company'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Issue Tracker' in response.data

    def test_login_invalid_password(self, client, user, tenant):
        response = client.post('/login', data={
            'email': 'john@test.com',
            'password': 'wrongpassword',
            'tenant_slug': 'test-company'
        })

        assert response.status_code == 200
        assert b'Invalid email or password' in response.data

    def test_login_nonexistent_tenant(self, client):
        response = client.post('/login', data={
            'email': 'john@test.com',
            'password': 'password123',
            'tenant_slug': 'nonexistent'
        })

        assert response.status_code == 200
        assert b'Workspace not found' in response.data

    def test_login_nonexistent_user(self, client, tenant):
        response = client.post('/login', data={
            'email': 'nonexistent@test.com',
            'password': 'password123',
            'tenant_slug': 'test-company'
        })

        assert response.status_code == 200
        assert b'Invalid email or password' in response.data

    def test_logout(self, client, authenticated_client):
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data
