from models import db, Comment


class CommentService:
    def create_comment(self, issue, user, content):
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
