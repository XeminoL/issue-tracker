"""Health, CSRF, and comment endpoint tests."""
import json


class TestHealth:
    def test_health_ok(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert data['database'] == 'up'


class TestCSRF:
    def test_login_form_rejects_missing_token(self, csrf_client):
        # With CSRF on, a form POST without a token must be rejected (400),
        # never processed as a login attempt.
        response = csrf_client.post('/login', data={
            'tenant_slug': 'acme',
            'email': 'a@b.com',
            'password': 'x',
        })
        assert response.status_code == 400

    def test_api_is_csrf_exempt(self, authenticated_client):
        # The JSON API is session-authenticated and exempt from CSRF, so a
        # POST with no token still works.
        response = authenticated_client.post('/api/issues',
            data=json.dumps({'title': 'No token needed', 'description': 'ok'}),
            content_type='application/json')
        assert response.status_code == 201


class TestComments:
    def _make_issue(self, client, tenant, user):
        from models import Issue
        from app import db
        issue = Issue(title='Has comments', tenant_id=tenant.id, created_by=user.id)
        db.session.add(issue)
        db.session.commit()
        return issue

    def test_add_and_get_comment(self, authenticated_client, tenant, user):
        issue = self._make_issue(authenticated_client, tenant, user)

        add = authenticated_client.post(f'/api/issues/{issue.id}/comments',
            data=json.dumps({'content': 'First comment'}),
            content_type='application/json')
        assert add.status_code == 201
        assert 'id' in json.loads(add.data)

        got = authenticated_client.get(f'/api/issues/{issue.id}/comments')
        assert got.status_code == 200
        comments = json.loads(got.data)
        assert len(comments) == 1
        assert comments[0]['content'] == 'First comment'

    def test_empty_comment_rejected(self, authenticated_client, tenant, user):
        issue = self._make_issue(authenticated_client, tenant, user)
        response = authenticated_client.post(f'/api/issues/{issue.id}/comments',
            data=json.dumps({'content': ''}),
            content_type='application/json')
        assert response.status_code == 400
