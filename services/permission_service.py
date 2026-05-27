from exceptions import ForbiddenError


class PermissionService:
    def is_admin(self, user):
        return user.role == 'admin'

    def is_member(self, user):
        return user.role in ['admin', 'member']

    def can_create_issue(self, user):
        return self.is_member(user)

    def can_edit_issue(self, user, issue):
        return self.is_admin(user) or issue.created_by == user.id

    def can_delete_issue(self, user, issue):
        return self.is_admin(user) or issue.created_by == user.id

    def require_can_create_issue(self, user):
        if not self.can_create_issue(user):
            raise ForbiddenError('Cannot create issues')

    def require_can_edit_issue(self, user, issue):
        if not self.can_edit_issue(user, issue):
            raise ForbiddenError('Cannot edit this issue')

    def require_can_delete_issue(self, user, issue):
        if not self.can_delete_issue(user, issue):
            raise ForbiddenError('Cannot delete this issue')

    def require_is_admin(self, user):
        if not self.is_admin(user):
            raise ForbiddenError('Admin access required')

    def require_can_assign_issue(self, user):
        self.require_is_admin(user)
