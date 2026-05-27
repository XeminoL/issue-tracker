import pytest
import json
from models import Issue


class TestIssueAPI:
    def test_create_issue(self, authenticated_client, tenant):
        response = authenticated_client.post('/api/issues',
            data=json.dumps({
                'title': 'Test Issue',
                'description': 'This is a test issue'
            }),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'id' in data
        assert data['message'] == 'Issue created'

        issue = Issue.query.filter_by(tenant_id=tenant.id).first()
        assert issue is not None
        assert issue.title == 'Test Issue'
        assert issue.status == 'open'

    def test_get_issues(self, authenticated_client, tenant, user):
        Issue.query.filter_by(tenant_id=tenant.id).delete()

        issue1 = Issue(
            title='Issue 1',
            description='First issue',
            status='open',
            tenant_id=tenant.id,
            created_by=user.id
        )
        issue2 = Issue(
            title='Issue 2',
            description='Second issue',
            status='closed',
            tenant_id=tenant.id,
            created_by=user.id
        )
        from app import db
        db.session.add(issue1)
        db.session.add(issue2)
        db.session.commit()

        response = authenticated_client.get('/api/issues')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]['title'] == 'Issue 1'
        assert data[1]['title'] == 'Issue 2'

    def test_get_single_issue(self, authenticated_client, tenant, user):
        issue = Issue(
            title='Single Issue',
            description='Test description',
            status='open',
            tenant_id=tenant.id,
            created_by=user.id
        )
        from app import db
        db.session.add(issue)
        db.session.commit()

        response = authenticated_client.get(f'/api/issues/{issue.id}')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['title'] == 'Single Issue'
        assert data['status'] == 'open'

    def test_update_issue(self, authenticated_client, tenant, user):
        issue = Issue(
            title='Original Title',
            description='Original description',
            status='open',
            tenant_id=tenant.id,
            created_by=user.id
        )
        from app import db
        db.session.add(issue)
        db.session.commit()

        response = authenticated_client.put(f'/api/issues/{issue.id}',
            data=json.dumps({
                'title': 'Updated Title',
                'status': 'closed'
            }),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Issue updated'

        updated_issue = Issue.query.get(issue.id)
        assert updated_issue.title == 'Updated Title'
        assert updated_issue.status == 'closed'

    def test_delete_issue(self, authenticated_client, tenant, user):
        issue = Issue(
            title='Issue to delete',
            description='This will be deleted',
            status='open',
            tenant_id=tenant.id,
            created_by=user.id
        )
        from app import db
        db.session.add(issue)
        db.session.commit()

        issue_id = issue.id

        response = authenticated_client.delete(f'/api/issues/{issue_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Issue deleted'

        deleted_issue = Issue.query.get(issue_id)
        assert deleted_issue is None

    def test_issue_isolation_between_tenants(self, authenticated_client, tenant, user):
        from app import db
        from models import Tenant

        issue = Issue(
            title='Tenant 1 Issue',
            description='This belongs to tenant 1',
            status='open',
            tenant_id=tenant.id,
            created_by=user.id
        )
        db.session.add(issue)
        db.session.commit()

        other_tenant = Tenant(name='Other Company', slug='other-company')
        db.session.add(other_tenant)
        db.session.commit()

        with authenticated_client.session_transaction() as sess:
            sess['tenant_id'] = other_tenant.id

        response = authenticated_client.get('/api/issues')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 0

    def test_get_issue_without_auth(self, client):
        response = client.get('/api/issues')
        assert response.status_code == 302
