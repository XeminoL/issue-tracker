from exceptions import ValidationError, NotFoundError
from models import db, Comment
from email_service import email_service


class CommentService:
    def create_comment(self, issue, user, content):
        if not content or not content.strip():
            raise ValidationError('content', 'Comment cannot be empty')

        comment = Comment(
            content=content,
            issue_id=issue.id,
            created_by=user.id
        )
        db.session.add(comment)
        db.session.commit()

        return comment

    def get_comments(self, issue):
        return Comment.query.filter_by(issue_id=issue.id).all()
