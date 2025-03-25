from . import db, bcrypt, login_manager
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password = db.Column(db.String(128))  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    
    def get_id(self):
        return self.id_usuario
    
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
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'))
    usuario = db.relationship('User', backref=db.backref('pacientes', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
        
    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if self.created_at:
            result['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            result['updated_at'] = self.updated_at.isoformat()
        return result
class Expediente(db.Model):
    __tablename__ = 'expedientes'
        
    id_expediente = db.Column(db.Integer, primary_key=True, index=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('pacientes.id_paciente', ondelete='CASCADE'))
    paciente = db.relationship('Paciente', backref=db.backref('expedientes', lazy=True))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.String(120))        
    
    def __init__(self, id_paciente, descripcion):
        self.id_paciente = id_paciente
        self.descripcion = descripcion
    
    @classmethod
    def create_expediente(cls, id_paciente, descripcion):
        expediente = cls(id_paciente=id_paciente, descripcion=descripcion)
        db.session.add(expediente)
        db.session.commit()
        return expediente
    
    @staticmethod
    def get_expediente_by_id(id_expediente):
        return Expediente.query.filter_by(id_expediente=id_expediente).first()

class ModificacionExpediente(db.Model):
    __tablename__ = 'modificaciones_expedientes'
    
    id_modificacion = db.Column(db.Integer, primary_key=True, index=True)
    id_expediente = db.Column(db.Integer, db.ForeignKey('expedientes.id_expediente', ondelete='CASCADE'))
    expediente = db.relationship('Expediente', backref=db.backref('modificaciones', lazy=True))
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.String(120))
    
    @staticmethod
    def get_modificacion_by_id(id_modificacion):
        return ModificacionExpediente.query.filter_by(id_modificacion=id_modificacion).first()
    
    @staticmethod
    def get_modificaciones_by_expediente(id_expediente):
        return ModificacionExpediente.query.filter_by(id_expediente=id_expediente).all()
    
    @staticmethod
    def create_modificacion_expediente(id_expediente, descripcion):
        modificacion = ModificacionExpediente(id_expediente=id_expediente, descripcion=descripcion)
        db.session.add(modificacion)
        db.session.commit()
        return modificacion
    

class HistoriaClinica(db.Model):
    __tablename__ = 'historias_clinicas'
    
    id_historia_clinica = db.Column(db.Integer, primary_key=True, index=True)
    id_expediente = db.Column(db.Integer, db.ForeignKey('expedientes.id_expediente', ondelete='CASCADE'))
    expediente = db.relationship('Expediente', backref=db.backref('historias_clinicas', lazy=True))
    motivo_consulta = db.Column(db.String(120))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def get_historia_clinica_by_id(id_historia_clinica):
        return HistoriaClinica.query.filter_by(id_historia_clinica=id_historia_clinica).first()
    

class AntecedentesPersonales(db.Model):
    __tablename__ = 'antecedentes_personales'
    
    id_antecedente_personal = db.Column(db.Integer, primary_key=True, index=True)
    id_expediente = db.Column(db.Integer, db.ForeignKey('expedientes.id_expediente', ondelete='CASCADE'))
    expediente = db.relationship('Expediente', backref=db.backref('antecedentes_personales', lazy=True))
    descripcion = db.Column(db.String(120))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)    
    
    
class AntecedentesFamiliares(db.Model):
    __tablename__ = 'antecedentes_familiares'
    
    id_antecedente_familiar = db.Column(db.Integer, primary_key=True, index=True)
    id_expediente = db.Column(db.Integer, db.ForeignKey('expedientes.id_expediente', ondelete='CASCADE'))
    expediente = db.relationship('Expediente', backref=db.backref('antecedentes_familiares', lazy=True))
    descripcion = db.Column(db.String(120))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)