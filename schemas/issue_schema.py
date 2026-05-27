from exceptions import ValidationError


class IssueSchema:
    @staticmethod
    def validate_create(data):
        title = data.get('title')
        if not title or not str(title).strip():
            raise ValidationError('title', 'Title is required')
        if len(title) > 200:
            raise ValidationError('title', 'Title must be less than 200 characters')
        return True

    @staticmethod
    def validate_update(data):
        if 'title' in data:
            title = data['title']
            if not title or not str(title).strip():
                raise ValidationError('title', 'Title is required')
            if len(title) > 200:
                raise ValidationError('title', 'Title must be less than 200 characters')
        if 'status' in data:
            status = data['status']
            if status not in ['open', 'closed']:
                raise ValidationError('status', 'Invalid status')
        return True

    @staticmethod
    def serialize(issue):
        return {
            'id': issue.id,
            'title': issue.title,
            'description': issue.description,
            'status': issue.status,
            'created_by': issue.created_by,
            'assigned_to': issue.assigned_to,
            'created_at': issue.created_at.isoformat(),
            'updated_at': issue.updated_at.isoformat(),
        }

    @staticmethod
    def serialize_list(issues):
        return [IssueSchema.serialize(issue) for issue in issues]
