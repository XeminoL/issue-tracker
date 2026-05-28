from werkzeug.security import generate_password_hash, check_password_hash


class AuthService:
    def hash_password(self, password):
        return generate_password_hash(password)

    def verify_password(self, password_hash, password):
        return check_password_hash(password_hash, password)
