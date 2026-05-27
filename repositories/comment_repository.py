from models import Comment, db
from repositories.base_repository import BaseRepository


class CommentRepository(BaseRepository):
    def __init__(self, db_instance, tenant_id):
        super().__init__(db_instance, Comment, tenant_id)

    def list_by_issue(self, issue_id):
        return Comment.query.filter_by(issue_id=issue_id).all()
