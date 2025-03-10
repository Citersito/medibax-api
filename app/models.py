from . import db, bcrypt, login_manager
from sqlalchemy import Column, Integer, String, ForeignKey
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password = db.Column(db.String(128))  
    
    def __init__(self, email, password):
        self.email = email
        if password:
            self.set_password(password) 
        
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
            
    @staticmethod
    def create_user(email, password):
        if User.get_user_by_email(email):
            raise ValueError("El usuario con este correo electrónico ya existe.")
        user = User(email, password)  
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Paciente(db.Model):
    __tablename__ = 'pacientes'
    
    id_paciente = db.Column(db.Integer, primary_key=True, index=True)
    nombre = db.Column(db.String(120))
    nombre_segundo = db.Column(db.String(120))
    apellido_paterno = db.Column(db.String(120))
    apellido_materno = db.Column(db.String(120))
    curp = db.Column(db.String(18), unique=True)
    telefono = db.Column(db.String(15))
    direccion = db.Column(db.String(120))
    estado = db.Column(db.String(120))
    ciudad = db.Column(db.String(120))
    estado_civil = db.Column(db.String(120))
    ocupacion = db.Column(db.String(120))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    usuario = db.relationship('User', backref=db.backref('pacientes', lazy=True))
    
    def __init__(self, nombre, apellido_paterno, apellido_materno, curp, telefono, direccion, estado, ciudad, estado_civil, ocupacion, id_usuario, nombre_segundo=None):
        self.nombre = nombre
        self.nombre_segundo = nombre_segundo
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.curp = curp
        self.telefono = telefono
        self.direccion = direccion
        self.estado = estado
        self.ciudad = ciudad
        self.estado_civil = estado_civil
        self.ocupacion = ocupacion
        self.id_usuario = id_usuario
        
    @staticmethod
    def create_paciente(nombre, apellido_paterno, apellido_materno, curp, telefono, direccion, estado, ciudad, estado_civil, ocupacion, id_usuario, nombre_segundo=None):
        if Paciente.get_paciente_by_curp(curp):
            raise ValueError("El paciente con este CURP ya existe.")
        paciente = Paciente(nombre, apellido_paterno, apellido_materno, curp, telefono, direccion, estado, ciudad, estado_civil, ocupacion, id_usuario, nombre_segundo)
        db.session.add(paciente)
        db.session.commit()
        return paciente
    
    @staticmethod
    def get_paciente_by_id(id_paciente):
        return Paciente.query.filter_by(id_paciente=id_paciente).first()
    
    @staticmethod
    def get_paciente_by_curp(curp):
        return Paciente.query.filter_by(curp=curp).first()
    
    def update_paciente(self, nombre=None, nombre_segundo=None, apellido_paterno=None, apellido_materno=None, curp=None, telefono=None, direccion=None, estado=None, ciudad=None, estado_civil=None, ocupacion=None):
        if nombre:
            self.nombre = nombre
        if nombre_segundo:
            self.nombre_segundo = nombre_segundo
        if apellido_paterno:
            self.apellido_paterno = apellido_paterno
        if apellido_materno:
            self.apellido_materno = apellido_materno
        if curp:
            self.curp = curp
        if telefono:
            self.telefono = telefono
        if direccion:
            self.direccion = direccion
        if estado:
            self.estado = estado
        if ciudad:
            self.ciudad = ciudad
        if estado_civil:
            self.estado_civil = estado_civil
        if ocupacion:
            self.ocupacion = ocupacion
        db.session.commit()
        return self
    
    def delete_paciente(self):
        db.session.delete(self)
        db.session.commit()