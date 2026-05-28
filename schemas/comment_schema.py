from exceptions import ValidationError


class CommentSchema:
    @staticmethod
    def validate_create(data):
        content = data.get('content')
        if not content or not str(content).strip():
            raise ValidationError('content', 'Comment cannot be empty')

    @staticmethod
    def serialize(comment):
        return {
            'id': comment.id,
            'content': comment.content,
            'issue_id': comment.issue_id,
            'created_by': comment.created_by,
            'created_at': comment.created_at.strftime('%Y-%m-%d - %H:%M:%S'),
        }

    @staticmethod
    def serialize_list(comments):
        return [CommentSchema.serialize(comment) for comment in comments]
