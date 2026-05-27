from exceptions import ValidationError


class CommentSchema:
    @staticmethod
    def validate_create(data):
        content = data.get('content')
        if not content or not str(content).strip():
            raise ValidationError('content', 'Comment cannot be empty')
        return True

    @staticmethod
    def serialize(comment):
        return {
            'id': comment.id,
            'content': comment.content,
            'created_by': comment.created_by,
            'issue_id': comment.issue_id,
            'created_at': comment.created_at.isoformat(),
        }

    @staticmethod
    def serialize_list(comments):
        return [CommentSchema.serialize(comment) for comment in comments]
