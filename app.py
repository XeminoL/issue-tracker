from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config
from models import db, User, Tenant
from exceptions import ValidationError, NotFoundError, ForbiddenError, ConflictError
from services import AuthService, PermissionService, IssueService, CommentService
from repositories import TenantRepository, IssueRepository
from schemas import IssueSchema, CommentSchema
from email_service import email_service


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

with app.app_context():
    db.create_all()

auth_service = AuthService()
permission_service = PermissionService()
issue_service = IssueService(permission_service)
comment_service = CommentService()


def get_current_user():
    user_id = session.get('user_id')
    return db.session.get(User, user_id) if user_id else None


def get_current_tenant():
    tenant_id = session.get('tenant_id')
    return db.session.get(Tenant, tenant_id) if tenant_id else None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        tenant = get_current_tenant()
        if not user or not tenant:
            session.clear()
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({'error': e.message, 'field': e.field}), 400


@app.errorhandler(NotFoundError)
def handle_not_found(e):
    return jsonify({'error': f'{e.resource_type} not found'}), 404


@app.errorhandler(ForbiddenError)
def handle_forbidden(e):
    return jsonify({'error': e.message}), 403


@app.errorhandler(ConflictError)
def handle_conflict(e):
    return jsonify({'error': e.message}), 409


@app.errorhandler(429)
def handle_ratelimit(e):
    return jsonify({'error': 'Rate limit exceeded. Too many requests.'}), 429


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.form
    try:
        tenant = TenantRepository(db).get_by_slug(data.get('tenant_slug'))
        user = User.query.filter_by(email=data.get('email'), tenant_id=tenant.id).first()

        if not user or not auth_service.verify_password(user.password_hash, data.get('password')):
            raise ValidationError('credentials', 'Invalid email or password')

        session['user_id'] = user.id
        session['tenant_id'] = tenant.id
        return redirect(url_for('dashboard'))
    except NotFoundError:
        return render_template('login.html', error='Workspace not found')
    except ValidationError as e:
        return render_template('login.html', error=e.message)


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def register():
    if request.method == 'GET':
        return render_template('register.html')

    data = request.form
    try:
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        tenant_name = data.get('tenant_name')
        tenant_slug = data.get('tenant_slug')

        if not all([name, email, password, tenant_name, tenant_slug]):
            raise ValidationError('fields', 'All fields are required')

        tenant_repo = TenantRepository(db)
        tenant = tenant_repo.create(tenant_name, tenant_slug)

        user = User(
            name=name,
            email=email,
            password_hash=auth_service.hash_password(password),
            tenant_id=tenant.id,
            role='admin'
        )
        db.session.add(user)
        db.session.commit()

        email_service.send_welcome_email(user.email, user.name, tenant.name)

        session['user_id'] = user.id
        session['tenant_id'] = tenant.id
        return redirect(url_for('dashboard'))
    except (ValidationError, ConflictError) as e:
        return render_template('register.html', error=e.message)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template(
        'dashboard.html',
        user=get_current_user(),
        tenant=get_current_tenant()
    )


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/api/issues', methods=['GET'])
@login_required
@limiter.limit("30 per minute")
def get_issues():
    tenant = get_current_tenant()
    issues = IssueRepository(db, tenant.id).list_all()
    return jsonify(IssueSchema.serialize_list(issues)), 200


@app.route('/api/issues', methods=['POST'])
@login_required
@limiter.limit("10 per minute")
def create_issue():
    data = request.get_json()
    IssueSchema.validate_create(data)

    issue = issue_service.create_issue(
        get_current_tenant(),
        get_current_user(),
        data.get('title'),
        data.get('description')
    )
    return jsonify({'id': issue.id, 'message': 'Issue created'}), 201


@app.route('/api/issues/<int:issue_id>', methods=['GET'])
@login_required
def get_issue(issue_id):
    tenant = get_current_tenant()
    issue = IssueRepository(db, tenant.id).get_by_id(issue_id)
    return jsonify(IssueSchema.serialize(issue)), 200


@app.route('/api/issues/<int:issue_id>', methods=['PUT'])
@login_required
@limiter.limit("10 per minute")
def update_issue(issue_id):
    tenant = get_current_tenant()
    data = request.get_json()
    IssueSchema.validate_update(data)

    issue = IssueRepository(db, tenant.id).get_by_id(issue_id)
    issue_service.update_issue(
        issue,
        get_current_user(),
        title=data.get('title'),
        description=data.get('description'),
        status=data.get('status')
    )
    return jsonify({'message': 'Issue updated'}), 200


@app.route('/api/issues/<int:issue_id>', methods=['DELETE'])
@login_required
@limiter.limit("5 per minute")
def delete_issue(issue_id):
    tenant = get_current_tenant()
    issue = IssueRepository(db, tenant.id).get_by_id(issue_id)
    issue_service.delete_issue(issue, get_current_user())
    return jsonify({'message': 'Issue deleted'}), 200


@app.route('/api/issues/<int:issue_id>/assign', methods=['POST'])
@login_required
def assign_issue(issue_id):
    tenant = get_current_tenant()
    data = request.get_json()

    issue = IssueRepository(db, tenant.id).get_by_id(issue_id)
    issue_service.assign_issue(issue, tenant, get_current_user(), data.get('assigned_to'))
    return jsonify({'message': 'Issue assigned'}), 200


@app.route('/api/issues/<int:issue_id>/comments', methods=['GET'])
@login_required
def get_comments(issue_id):
    tenant = get_current_tenant()
    issue = IssueRepository(db, tenant.id).get_by_id(issue_id)
    comments = comment_service.get_comments(issue)
    return jsonify(CommentSchema.serialize_list(comments)), 200


@app.route('/api/issues/<int:issue_id>/comments', methods=['POST'])
@login_required
def add_comment(issue_id):
    tenant = get_current_tenant()
    data = request.get_json()
    CommentSchema.validate_create(data)

    issue = IssueRepository(db, tenant.id).get_by_id(issue_id)
    comment = comment_service.create_comment(issue, get_current_user(), data.get('content'))
    return jsonify({'id': comment.id, 'message': 'Comment added'}), 201


if __name__ == '__main__':
    app.run(debug=Config.DEBUG)
