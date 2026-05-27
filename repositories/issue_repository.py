from models import Issue, db
from repositories.base_repository import BaseRepository


class IssueRepository(BaseRepository):
    def __init__(self, db_instance, tenant_id):
        super().__init__(db_instance, Issue, tenant_id)

    def list_all_issues(self):
        return self.list_all()

    def list_by_status(self, status):
        return self._filter_by_tenant(
            Issue.query
        ).filter_by(status=status).all()

    def list_by_creator(self, user_id):
        return self._filter_by_tenant(
            Issue.query
        ).filter_by(created_by=user_id).all()

    def list_assigned_to_user(self, user_id):
        return self._filter_by_tenant(
            Issue.query
        ).filter_by(assigned_to=user_id).all()
