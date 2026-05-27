from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy


def utc_now():
    return datetime.now(timezone.utc)


db = SQLAlchemy()


class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    users = db.relationship(
        'User',
        backref='tenant',
        lazy=True,
        cascade='all, delete-orphan'
    )
    issues = db.relationship(
        'Issue',
        backref='tenant',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Tenant {self.name}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='member')
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'),
                          nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    __table_args__ = (
        db.UniqueConstraint('email', 'tenant_id',
                           name='unique_email_per_tenant'),
    )

    def __repr__(self):
        return f'<User {self.name}>'

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='open')
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'),
                          nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'),
                           nullable=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'),
                            nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    comments = db.relationship(
        'Comment',
        backref='issue',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Issue {self.title}>'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'),
                         nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'),
                           nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    creator = db.relationship('User', backref='comments')

    def __repr__(self):
        return f'<Comment {self.id}>'
