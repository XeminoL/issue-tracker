from models import Tenant, db
from exceptions import NotFoundError, ConflictError


class TenantRepository:
    def __init__(self, db_instance):
        self.db = db_instance
        self.model = Tenant

    def get_by_id(self, id):
        result = self.model.query.filter_by(id=id).first()
        if not result:
            raise NotFoundError('Tenant', id)
        return result

    def get_by_slug(self, slug):
        result = self.model.query.filter_by(slug=slug).first()
        if not result:
            raise NotFoundError('Tenant', slug)
        return result

    def create(self, name, slug):
        if self.model.query.filter_by(slug=slug).first():
            raise ConflictError('Tenant with this slug already exists')

        tenant = self.model(name=name, slug=slug)
        self.db.session.add(tenant)
        self.db.session.commit()
        return tenant

    def list_all(self):
        return self.model.query.all()
