from . import db, bcrypt, login_manager
from sqlalchemy import Column, Integer, String
from flask_login import UserMixin

class User(UserMixin,db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True, index=True)
    email = Column(String(120), unique=True, index=True)
    password = Column(String(128))  
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        if password:
            self.setPassword(password) 
        
    def setPassword(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        
    def checkPassword(self, password):
        return bcrypt.check_password_hash(self.password, password)
            
    @staticmethod
    def create_user(username, email, password):
        user = User(username, email, password)  
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))