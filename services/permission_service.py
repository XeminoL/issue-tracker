from exceptions import ForbiddenError


class PermissionService:
    def is_admin(self, user):
        return user.role == 'admin'

    def can_edit_issue(self, user, issue):
        return self.is_admin(user) or issue.created_by == user.id

    def require_can_create_issue(self, user):
        if user.role not in ['admin', 'member']:
            raise ForbiddenError('Cannot create issues')

    def require_can_edit_issue(self, user, issue):
        if not self.can_edit_issue(user, issue):
            raise ForbiddenError('Cannot edit this issue')

    def require_can_delete_issue(self, user, issue):
        if not self.can_edit_issue(user, issue):
            raise ForbiddenError('Cannot delete this issue')

    def require_is_admin(self, user):
        if not self.is_admin(user):
            raise ForbiddenError('Admin access required')
