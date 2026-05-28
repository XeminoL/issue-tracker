from exceptions import NotFoundError


class BaseRepository:
    def __init__(self, db, model, tenant_id):
        self.db = db
        self.model = model
        self.tenant_id = tenant_id

    def _filter_by_tenant(self, query):
        return query.filter_by(tenant_id=self.tenant_id)

    def get_by_id(self, id):
        result = self._filter_by_tenant(self.model.query).filter_by(id=id).first()
        if not result:
            raise NotFoundError(self.model.__name__, id)
        return result

    def list_all(self):
        return self._filter_by_tenant(self.model.query).all()
