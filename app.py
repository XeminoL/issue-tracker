from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for
)
from functools import wraps
from config import Config
from models import db, User, Tenant
from exceptions import (
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
)
from services.auth_service import AuthService
from services.permission_service import PermissionService
from services.issue_service import IssueService
from services.comment_service import CommentService
from repositories.tenant_repository import TenantRepository
from repositories.issue_repository import IssueRepository
from schemas.issue_schema import IssueSchema
from schemas.comment_schema import CommentSchema
from email_service import email_service

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

auth_service = AuthService()
permission_service = PermissionService()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or 'tenant_id' not in session:
            auth_token = request.cookies.get('auth_token')
            if auth_token:
                payload = auth_service.verify_token(auth_token)
                if payload:
                    session['user_id'] = payload['user_id']
                    session['tenant_id'] = payload['tenant_id']
                else:
                    return redirect(url_for('login'))
            else:
                return redirect(url_for('login'))

        user = get_current_user()
        tenant = get_current_tenant()
        if not user or not tenant:
            session.clear()
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


def get_current_tenant():
    if 'tenant_id' in session:
        return Tenant.query.get(session['tenant_id'])
    return None


@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({'error': e.message, 'field': e.field}), 400


@app.errorhandler(NotFoundError)
def handle_not_found(e):
    return jsonify({
        'error': f'{e.resource_type} not found'
    }), 404


@app.errorhandler(ForbiddenError)
def handle_forbidden(e):
    return jsonify({'error': e.message}), 403


@app.errorhandler(UnauthorizedError)
def handle_unauthorized(e):
    return jsonify({'error': e.message}), 401


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.form
            tenant_repo = TenantRepository(db)
            tenant = tenant_repo.get_by_slug(data.get('tenant_slug'))

            user = User.query.filter_by(
                email=data.get('email'),
                tenant_id=tenant.id
            ).first()

            if not user or not auth_service.verify_password(data.get('password'), user.password_hash):
                raise ValidationError('credentials', 'Invalid email or password')

            session['user_id'] = user.id
            session['tenant_id'] = tenant.id

            response = redirect(url_for('dashboard'))

            remember_me = data.get('remember_me') == 'on'
            if remember_me:
                token = auth_service.generate_token(user.id, tenant.id, expires_in=30*24*3600)
                response.set_cookie(
                    'auth_token',
                    token,
                    max_age=30*24*3600,
                    httponly=True,
                    samesite='Lax'
                )

            return response
        except NotFoundError:
            raise
        except ValidationError as e:
            return render_template(
                'login.html',
                error=e.message
            )

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            data = request.form

            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            tenant_name = data.get('tenant_name')
            tenant_slug = data.get('tenant_slug')

            if not name or not email or not password or not tenant_name or not tenant_slug:
                raise ValidationError('fields', 'All fields are required')

            tenant_repo = TenantRepository(db)
            existing_tenant = Tenant.query.filter_by(slug=tenant_slug).first()
            if existing_tenant:
                raise ConflictError('Tenant already exists')

            tenant = tenant_repo.create(tenant_name, tenant_slug)

            existing_user = User.query.filter_by(email=email, tenant_id=tenant.id).first()
            if existing_user:
                raise ConflictError('User already exists')

            password_hash = auth_service.hash_password(password)
            user = User(
                name=name,
                email=email,
                password_hash=password_hash,
                tenant_id=tenant.id,
                role='admin'
            )
            db.session.add(user)
            db.session.commit()

            email_service.send_welcome_email(
                user.email,
                user.name,
                tenant.name
            )

            session['user_id'] = user.id
            session['tenant_id'] = tenant.id
            return redirect(url_for('dashboard'))
        except (ValidationError, ConflictError) as e:
            return render_template(
                'register.html',
                error=e.message if hasattr(e, 'message') else str(e)
            )

    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    tenant = get_current_tenant()
    return render_template('dashboard.html', user=user, tenant=tenant)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    response = redirect(url_for('login'))
    response.delete_cookie('auth_token')
    return response


@app.route('/api/issues', methods=['GET'])
@login_required
def get_issues():
    tenant = get_current_tenant()
    issue_repo = IssueRepository(db, tenant.id)
    issues = issue_repo.list_all_issues()
    return jsonify(IssueSchema.serialize_list(issues)), 200


@app.route('/api/issues', methods=['POST'])
@login_required
def create_issue():
    user = get_current_user()
    tenant = get_current_tenant()
    data = request.get_json()

    IssueSchema.validate_create(data)

    issue_service = IssueService(permission_service)
    issue = issue_service.create_issue(
        tenant,
        user,
        data.get('title'),
        data.get('description')
    )

    return jsonify({'id': issue.id, 'message': 'Issue created'}), 201


@app.route('/api/issues/<int:issue_id>', methods=['GET'])
@login_required
def get_issue(issue_id):
    tenant = get_current_tenant()
    issue_repo = IssueRepository(db, tenant.id)
    issue = issue_repo.get_by_id(issue_id)
    return jsonify(IssueSchema.serialize(issue)), 200


@app.route('/api/issues/<int:issue_id>', methods=['PUT'])
@login_required
def update_issue(issue_id):
    user = get_current_user()
    tenant = get_current_tenant()
    data = request.get_json()

    issue_repo = IssueRepository(db, tenant.id)
    issue = issue_repo.get_by_id(issue_id)

    IssueSchema.validate_update(data)

    issue_service = IssueService(permission_service)
    issue = issue_service.update_issue(
        issue,
        tenant,
        user,
        title=data.get('title'),
        description=data.get('description'),
        status=data.get('status')
    )

    return jsonify({'message': 'Issue updated'}), 200


@app.route('/api/issues/<int:issue_id>', methods=['DELETE'])
@login_required
def delete_issue(issue_id):
    user = get_current_user()
    tenant = get_current_tenant()

    issue_repo = IssueRepository(db, tenant.id)
    issue = issue_repo.get_by_id(issue_id)

    issue_service = IssueService(permission_service)
    issue_service.delete_issue(issue, user)

    return jsonify({'message': 'Issue deleted'}), 200


@app.route('/api/issues/<int:issue_id>/assign', methods=['POST'])
@login_required
def assign_issue(issue_id):
    user = get_current_user()
    tenant = get_current_tenant()
    data = request.get_json()

    issue_repo = IssueRepository(db, tenant.id)
    issue = issue_repo.get_by_id(issue_id)

    issue_service = IssueService(permission_service)
    issue = issue_service.assign_issue(
        issue,
        tenant,
        user,
        data.get('assigned_to')
    )

    return jsonify({'message': 'Issue assigned'}), 200


@app.route('/api/issues/<int:issue_id>/comments', methods=['GET'])
@login_required
def get_comments(issue_id):
    tenant = get_current_tenant()
    issue_repo = IssueRepository(db, tenant.id)
    issue = issue_repo.get_by_id(issue_id)

    comment_service = CommentService()
    comments = comment_service.get_comments(issue)

    return jsonify(CommentSchema.serialize_list(comments)), 200


@app.route('/api/issues/<int:issue_id>/comments', methods=['POST'])
@login_required
def add_comment(issue_id):
    user = get_current_user()
    tenant = get_current_tenant()
    data = request.get_json()

    issue_repo = IssueRepository(db, tenant.id)
    issue = issue_repo.get_by_id(issue_id)

    CommentSchema.validate_create(data)

    comment_service = CommentService()
    comment = comment_service.create_comment(
        issue,
        user,
        data.get('content')
    )

    return jsonify({
        'id': comment.id,
        'message': 'Comment added'
    }), 201


if __name__ == '__main__':
    app.run(debug=Config.DEBUG)
