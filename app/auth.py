from flask import request, jsonify, current_app
from flask_restx import Namespace, Resource, fields
from flask_login import login_user, logout_user, login_required
from app.models import User
import re

auth = Namespace('auth', description='Auth operations')

auth_model = auth.model('Auth', {
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Password'),
})

def is_valid_email(email):
    """Validate the email format."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def is_valid_password(password):
    """Validate the password length and complexity."""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True

@auth.route('/signup')
class SignUp(Resource):
    @auth.expect(auth_model)
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not is_valid_email(email):
            return {'message': 'Invalid email format'}, 400

        if not is_valid_password(password):
            return {'message': 'Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, and one number'}, 400
        
        if User.query.filter_by(email=email).first():
            return {'message': 'User already exists'}, 409
        
        new_user = User.create_user(email=email, password=password)
        return {'message': 'User created successfully', 'user': new_user.email}, 201
        

@auth.route('/login')
class Login(Resource):
    @auth.expect(auth_model)
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not is_valid_email(email):
            return {'message': 'Invalid email format'}, 400

        if not is_valid_password(password):
            return {'message': 'Invalid password format'}, 400

        user = User.query.filter_by(email=email).first()
        
        if user and user.checkPassword(password):
            login_user(user)
            return {'message': 'Login successful', 'user': user.email}, 200
        
        return {'message': 'Invalid email or password'}, 401
    
@auth.route('/logout')
class Logout(Resource):
    @login_required
    def post(self):
        logout_user()
        return {'message': 'Logout successful'}, 200
    
def init_auth_routes(api):
    api.add_namespace(auth)