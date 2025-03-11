from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from app.models import User, Paciente
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import re

auth = Namespace('auth', description='Auth operations')

auth_model = auth.model('Auth', {
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Password'),
})

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def is_valid_password(password):
    if len(password) < 7:
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
            return {'message': 'Password must be at least 7 characters long, contain at least one uppercase letter, one lowercase letter, and one number'}, 400
        
        if User.query.filter_by(email=email).first():
            return {'message': 'User already exists'}, 409
        
        new_user = User.create_user(email=email, password=password)
        new_Paciente = Paciente.create_paciente(nombre=None, apellido_paterno=None, apellido_materno=None, curp=None, telefono=None, direccion=None, estado=None, ciudad=None, estado_civil=None, ocupacion=None, id_usuario=new_user.id_usuario)
        access_token = create_access_token(identity=new_user.id_usuario)
        
        return {'message': 'User created successfully', 'user': new_user.email, 'access_token': access_token}, 201

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
        
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id_usuario)
            return {'message': 'Login successful', 'user': user.email, 'access_token': access_token}, 200
        
        return {'message': 'Invalid email or password'}, 401

@auth.route('/logout')
class Logout(Resource):
    @jwt_required()
    def post(self):
        # No need to logout with JWT; just remove the token on the client side
        return {'message': 'Logout successful'}, 200
    
@auth.route('/protected')
class Protected(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return {'message': f'Hello, user {current_user}'}, 200

def init_auth_routes(api):
    api.add_namespace(auth)