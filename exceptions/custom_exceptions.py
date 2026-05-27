class ValidationError(Exception):
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f'{field}: {message}')


class NotFoundError(Exception):
    def __init__(self, resource_type, resource_id):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f'{resource_type} {resource_id} not found')


class UnauthorizedError(Exception):
    def __init__(self, message='Authentication required'):
        self.message = message
        super().__init__(message)


class ForbiddenError(Exception):
    def __init__(self, message='Permission denied'):
        self.message = message
        super().__init__(message)


class ConflictError(Exception):
    def __init__(self, message='Resource already exists'):
        self.message = message
        super().__init__(message)
