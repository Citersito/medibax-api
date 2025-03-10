from flask import request, jsonify, current_app
from flask_restx import Namespace, Resource, fields
from flask_login import login_user, logout_user, login_required
from app.models import User

auth = Namespace('auth', description='Auth operations')

auth_model = auth.model('SignUp', {
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Password'),
})

@auth.route('/signup')
class SignUp(Resource):
    @auth.expect(auth_model)
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return {'message': 'User already exists'}, 409
        
        new_user = User.create_user(username=username, email=email, password=password)
        return {'message': 'User created successfully', 'user': new_user.username}, 201
        

@auth.route('/login')
class Login(Resource):
    @auth.expect(auth_model)
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.checkPassword(password):
            login_user(user)
            return {'message': 'Login successful', 'user': user.username}, 200
        
        return {'message': 'Invalid username or password'}, 401
    
@auth.route('/logout')
class Logout(Resource):
    @login_required
    def post(self):
        logout_user()
        return {'message': 'Logout successful'}, 200
    
def init_auth_routes(api):
    api.add_namespace(auth)