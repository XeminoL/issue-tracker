from exceptions import ValidationError
from schemas.base_schema import BaseSchema
from models import STATUS_OPEN, STATUS_CLOSED


def _validate_title(title):
    if not title or not str(title).strip():
        raise ValidationError('title', 'Title is required')
    if len(title) > 200:
        raise ValidationError('title', 'Title must be less than 200 characters')


class IssueSchema(BaseSchema):
    @staticmethod
    def validate_create(data):
        _validate_title(data.get('title'))

    @staticmethod
    def validate_update(data):
        if 'title' in data:
            _validate_title(data['title'])
        if 'status' in data and data['status'] not in [STATUS_OPEN, STATUS_CLOSED]:
            raise ValidationError('status', f'Invalid status. Must be {STATUS_OPEN} or {STATUS_CLOSED}')

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

