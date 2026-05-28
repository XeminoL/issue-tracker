from exceptions import ValidationError


def _validate_title(title):
    if not title or not str(title).strip():
        raise ValidationError('title', 'Title is required')
    if len(title) > 200:
        raise ValidationError('title', 'Title must be less than 200 characters')


class IssueSchema:
    @staticmethod
    def validate_create(data):
        _validate_title(data.get('title'))

    @staticmethod
    def validate_update(data):
        if 'title' in data:
            _validate_title(data['title'])
        if 'status' in data and data['status'] not in ['open', 'closed']:
            raise ValidationError('status', 'Invalid status')

    @staticmethod
    def serialize(issue):
        return {
            'id': issue.id,
            'title': issue.title,
            'description': issue.description,
            'status': issue.status,
            'created_by': issue.created_by,
            'assigned_to': issue.assigned_to,
            'created_at': issue.created_at.strftime('%Y-%m-%d - %H:%M:%S'),
            'updated_at': issue.updated_at.strftime('%Y-%m-%d - %H:%M:%S'),
        }

    @staticmethod
    def serialize_list(issues):
        return [IssueSchema.serialize(issue) for issue in issues]
