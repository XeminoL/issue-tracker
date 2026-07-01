from exceptions import NotFoundError
from models import db, Issue, User
from services.email_service import email_service


class IssueService:
    def __init__(self, permission_service):
        self.permissions = permission_service

    def create_issue(self, tenant, user, title, description):
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

    def update_issue(self, issue, user, title=None, description=None, status=None):
        self.permissions.require_can_edit_issue(user, issue)

        if title is not None:
            issue.title = title
        if description is not None:
            issue.description = description
        if status is not None:
            issue.status = status

        db.session.commit()
        return issue

    def delete_issue(self, issue, user):
        self.permissions.require_can_delete_issue(user, issue)
        db.session.delete(issue)
        db.session.commit()

    def assign_issue(self, issue, tenant, user, assigned_to_id):
        self.permissions.require_is_admin(user)

        assigned_user = User.query.filter_by(
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
