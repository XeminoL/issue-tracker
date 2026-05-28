from models import Tenant
from exceptions import NotFoundError, ConflictError


class TenantRepository:
    def __init__(self, db):
        self.db = db

    def get_by_slug(self, slug):
        tenant = Tenant.query.filter_by(slug=slug).first()
        if not tenant:
            raise NotFoundError('Tenant', slug)
        return tenant

    def create(self, name, slug):
        if Tenant.query.filter_by(slug=slug).first():
            raise ConflictError('Tenant already exists')

        tenant = Tenant(name=name, slug=slug)
        self.db.session.add(tenant)
        self.db.session.commit()
        return tenant
