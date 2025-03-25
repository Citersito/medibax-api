from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
load_dotenv()
from config import Config

db = SQLAlchemy()
api = Api()
bcrypt = Bcrypt()
jwt = JWTManager()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)
    
    # Inicializacion de servicios
    db.init_app(app)
    api.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    login_manager.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})  
    
    # Inicializacion de modelos
    with app.app_context():
        from app.models import User
        db.create_all()
    
    # Inicializacion de rutas
    from app.routes import init_routes
    from app.auth import init_auth_routes
    from app.expediente import init_expediente_routes
    from app.ai import init_ai_routes
    init_auth_routes(api)
    init_routes(api)
    init_expediente_routes(api)
    init_ai_routes(api)

    
    return app