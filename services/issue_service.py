from exceptions import (
    ValidationError,
    NotFoundError,
    ForbiddenError
)
from models import db, Issue
from email_service import email_service


class IssueService:
    def __init__(self, permission_service=None):
        self.permissions = permission_service

    def create_issue(self, tenant, user, title, description):
        if not title or not title.strip():
            raise ValidationError('title', 'Title is required')
        if len(title) > 200:
            raise ValidationError('title', 'Title too long (max 200)')

        self.permissions.require_can_create_issue(user)

        issue = Issue(
            title=title,
            description=description,
            tenant_id=tenant.id,
            created_by=user.id
        )
        db.session.add(issue)
        db.session.commit()

        email_service.send_issue_created_email(
            user.email,
            issue.title,
            issue.description,
            tenant.name
        )
        return issue

    def get_issue(self, issue_id, tenant):
        issue = Issue.query.filter_by(
            id=issue_id,
            tenant_id=tenant.id
        ).first()
        if not issue:
            raise NotFoundError('Issue', issue_id)
        return issue

    def list_issues(self, tenant):
        return Issue.query.filter_by(tenant_id=tenant.id).all()

    def update_issue(self, issue, tenant, user, title=None,
                     description=None, status=None):
        self.permissions.require_can_edit_issue(user, issue)

        if title is not None:
            if not title or not title.strip():
                raise ValidationError('title', 'Title is required')
            if len(title) > 200:
                raise ValidationError('title', 'Title too long')
            issue.title = title

        if description is not None:
            issue.description = description

        if status is not None:
            if status not in ['open', 'closed']:
                raise ValidationError('status', 'Invalid status')
            issue.status = status

        db.session.commit()
        return issue

    def delete_issue(self, issue, user):
        self.permissions.require_can_delete_issue(user, issue)
        db.session.delete(issue)
        db.session.commit()

    def assign_issue(self, issue, tenant, user, assigned_to_id):
        self.permissions.require_can_assign_issue(user)

        assigned_user = Issue.query.filter_by(
            id=assigned_to_id,
            tenant_id=tenant.id
        ).first()
        if not assigned_user:
            raise NotFoundError('User', assigned_to_id)

        issue.assigned_to = assigned_to_id
        db.session.commit()

        email_service.send_issue_assigned_email(
            assigned_user.email,
            issue.title,
            user.name,
            tenant.name
        )
        return issue
