from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from config import Config
from models import utc_now


class AuthService:
    def hash_password(self, password):
        return generate_password_hash(password)

    def verify_password(self, password_hash, password):
        return check_password_hash(password_hash, password)

    def generate_token(self, user_id, tenant_id, expires_in=3600):
        payload = {
            'user_id': user_id,
            'tenant_id': tenant_id,
            'exp': utc_now() + timedelta(seconds=expires_in)
        }
        return jwt.encode(
            payload,
            Config.SECRET_KEY,
            algorithm='HS256'
        )

    def verify_token(self, token):
        try:
            payload = jwt.decode(
                token,
                Config.SECRET_KEY,
                algorithms=['HS256']
            )
            return payload
        except jwt.InvalidTokenError:
            return None
