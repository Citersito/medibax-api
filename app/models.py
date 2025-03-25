from . import db, bcrypt, login_manager
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
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
        return self.id
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Paciente(db.Model):
    __tablename__ = 'pacientes'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    nombre = db.Column(db.String(120), nullable=False)
    nombre_segundo = db.Column(db.String(120), nullable=True)
    apellido_paterno = db.Column(db.String(120), nullable=False)
    apellido_materno = db.Column(db.String(120), nullable=False)
    curp = db.Column(db.String(18), unique=True, nullable=False)
    telefono = db.Column(db.String(15), nullable=True)
    direccion = db.Column(db.String(120), nullable=True)
    estado = db.Column(db.String(120), nullable=True)
    ciudad = db.Column(db.String(120), nullable=True)
    estado_civil = db.Column(db.String(120), nullable=True)
    ocupacion = db.Column(db.String(120), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=True)
    usuario = db.relationship('User', backref=db.backref('pacientes', lazy='dynamic'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, nombre, apellido_paterno, apellido_materno, curp, telefono, direccion, estado, ciudad, estado_civil, ocupacion, usuario_id=None, nombre_segundo=None):
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
        self.usuario_id = usuario_id
        
    @staticmethod
    def create_paciente(nombre, apellido_paterno, apellido_materno, curp, telefono, direccion, estado, ciudad, estado_civil, ocupacion, usuario_id=None, nombre_segundo=None):
        paciente = Paciente(nombre, apellido_paterno, apellido_materno, curp, telefono, direccion, estado, ciudad, estado_civil, ocupacion, usuario_id, nombre_segundo)
        db.session.add(paciente)
        db.session.commit()
        return paciente
    
    @staticmethod
    def get_paciente_by_id(id):
        return Paciente.query.filter_by(id=id).first()
    
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
        
    id = db.Column(db.Integer, primary_key=True, index=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id', ondelete='CASCADE'), nullable=False)
    paciente = db.relationship('Paciente', backref=db.backref('expediente', uselist=False))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    descripcion = db.Column(db.String(120), nullable=True)        
    
    @staticmethod
    def create_expediente(paciente_id, descripcion):
        expediente = Expediente(paciente_id=paciente_id, descripcion=descripcion)
        db.session.add(expediente)
        db.session.commit()
        return expediente
    
    def update_expediente(self, descripcion):
        self.descripcion = descripcion
        db.session.commit()
        return self
    
    @staticmethod
    def get_expediente_by_id(id):
        return Expediente.query.filter_by(id=id).first()
    
    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if self.fecha_creacion:
            result['fecha_creacion'] = self.fecha_creacion.isoformat()
        return result


class ModificacionExpediente(db.Model):
    __tablename__ = 'modificaciones_expedientes'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    expediente_id = db.Column(db.Integer, db.ForeignKey('expedientes.id', ondelete='CASCADE'), nullable=False)
    expediente = db.relationship('Expediente', backref=db.backref('modificaciones', lazy='dynamic'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True) 
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    descripcion = db.Column(db.String(120), nullable=True)
    tipo_modificacion = db.Column(db.String(50), nullable=False)  # Nuevo campo
    
    @staticmethod
    def create_modificacion_expediente(expediente_id, descripcion, tipo_modificacion):
        modificacion = ModificacionExpediente(expediente_id=expediente_id, descripcion=descripcion, tipo_modificacion=tipo_modificacion)
        db.session.add(modificacion)
        db.session.commit()
        return modificacion
    
    @staticmethod
    def get_modificacion_by_id(id):
        return ModificacionExpediente.query.filter_by(id=id).first()
    
    @staticmethod
    def get_modificaciones_by_expediente(expediente_id):
        return ModificacionExpediente.query.filter_by(expediente_id=expediente_id).all()
    
    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if self.fecha_modificacion:
            result['fecha_modificacion'] = self.fecha_modificacion.isoformat()
        return result

class HistoriaClinica(db.Model):
    __tablename__ = 'historias_clinicas'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    expediente_id = db.Column(db.Integer, db.ForeignKey('expedientes.id', ondelete='CASCADE'), nullable=False)
    expediente = db.relationship('Expediente', backref=db.backref('historias_clinicas', lazy='dynamic'))
    motivo_consulta = db.Column(db.String(120), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    @staticmethod
    def get_historia_clinica_by_id(id):
        return HistoriaClinica.query.filter_by(id=id).first()
    
    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if self.fecha_registro:
            result['fecha_registro'] = self.fecha_registro.isoformat()
        return result

class AntecedentesPersonales(db.Model):
    __tablename__ = 'antecedentes_personales'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    expediente_id = db.Column(db.Integer, db.ForeignKey('expedientes.id', ondelete='CASCADE'), nullable=False)
    expediente = db.relationship('Expediente', backref=db.backref('antecedentes_personales', lazy='dynamic'))
    descripcion = db.Column(db.String(120), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if self.fecha_registro:
            result['fecha_registro'] = self.fecha_registro.isoformat()
        return result

class AntecedentesFamiliares(db.Model):
    __tablename__ = 'antecedentes_familiares'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    expediente_id = db.Column(db.Integer, db.ForeignKey('expedientes.id', ondelete='CASCADE'), nullable=False)
    expediente = db.relationship('Expediente', backref=db.backref('antecedentes_familiares', lazy='dynamic'))
    descripcion = db.Column(db.String(120), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if self.fecha_registro:
            result['fecha_registro'] = self.fecha_registro.isoformat()
        return result


class Diagnostico(db.Model):
    __tablename__ = 'diagnosticos'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    expediente_id = db.Column(db.Integer, db.ForeignKey('expedientes.id', ondelete='CASCADE'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)  # Médico que diagnosticó
    expediente = db.relationship('Expediente', backref=db.backref('diagnosticos', lazy='dynamic'))
    enfermedad = db.Column(db.String(120), nullable=False)
    fecha_diagnostico = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    
    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if self.fecha_diagnostico:
            result['fecha_diagnostico'] = self.fecha_diagnostico.isoformat()
        return result
    
class Tratamiento(db.Model):
    __tablename__ = 'tratamientos'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    expediente_id = db.Column(db.Integer, db.ForeignKey('expedientes.id', ondelete='CASCADE'), nullable=False)
    expediente = db.relationship('Expediente', backref=db.backref('tratamientos', lazy='dynamic'))
    descripcion = db.Column(db.String(120), nullable=True)
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    
    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if self.fecha_inicio:
            result['fecha_inicio'] = self.fecha_inicio.isoformat()
        if self.fecha_fin:
            result['fecha_fin'] = self.fecha_fin.isoformat()
        return result
    
class ExamenesMedicos(db.Model):
    __tablename__ = 'examenes_medicos'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    expediente_id = db.Column(db.Integer, db.ForeignKey('expedientes.id', ondelete='CASCADE'), nullable=False)
    expediente = db.relationship('Expediente', backref=db.backref('examenes_medicos', lazy='dynamic'))
    tipo_examen = db.Column(db.String(120), nullable=False)
    resultado = db.Column(db.String(120), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if self.fecha_registro:
            result['fecha_registro'] = self.fecha_registro.isoformat()
        return result
    
class Intervenciones(db.Model):
    __tablename__ = 'intervenciones'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    expediente_id = db.Column(db.Integer, db.ForeignKey('expedientes.id', ondelete='CASCADE'), nullable=False)
    expediente = db.relationship('Expediente', backref=db.backref('intervenciones', lazy='dynamic'))
    descripcion = db.Column(db.String(120), nullable=True)
    fecha_intervencion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    medico_responsable = db.Column(db.String(120), nullable=True)
    tipo_intervencion = db.Column(db.String(120), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if self.fecha_registro:
            result['fecha_registro'] = self.fecha_registro.isoformat()
        return result
    
class ConsentimientosInformados(db.Model):
    __tablename__ = 'consentimientos_informados'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    expediente_id = db.Column(db.Integer, db.ForeignKey('expedientes.id', ondelete='CASCADE'), nullable=False)
    expediente = db.relationship('Expediente', backref=db.backref('consentimientos_informados', lazy='dynamic'))
    descripcion = db.Column(db.String(120), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if self.fecha_registro:
            result['fecha_registro'] = self.fecha_registro.isoformat()
        return result