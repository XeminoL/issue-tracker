from models import Issue
from repositories.base_repository import BaseRepository


class IssueRepository(BaseRepository):
    def __init__(self, db, tenant_id):
        super().__init__(db, Issue, tenant_id)
