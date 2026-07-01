class BaseSchema:
    @classmethod
    def serialize_list(cls, items):
        return [cls.serialize(item) for item in items]
