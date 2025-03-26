from flask_restx import Namespace, Resource, fields
from flask import request, jsonify, send_file
import qrcode
import io
import uuid
from .models import Paciente, Expediente, ModificacionExpediente, HistoriaClinica, AntecedentesPersonales, AntecedentesFamiliares, User

expediente = Namespace('expediente', description='Expediente operations')

# Modelos de datos
paciente_model = expediente.model('Paciente', {
    'nombre': fields.String(),
    'nombre_segundo': fields.String(),
    'apellido_paterno': fields.String(),
    'apellido_materno': fields.String(),
    'curp': fields.String(),
    'telefono': fields.String(),
    'direccion': fields.String(),
    'estado': fields.String(),
    'ciudad': fields.String(),
    'estado_civil': fields.String(),
    'ocupacion': fields.String(),
    'id_usuario': fields.Integer(required=True, description='ID del usuario asociado'),
})

expediente_model = expediente.model('Expediente', {
    'id_paciente': fields.Integer(required=True, description='ID del paciente asociado'),
    'descripcion': fields.String(),
})

modificacion_expediente_model = expediente.model('ModificacionExpediente', {
    'id_expediente': fields.Integer(required=True, description='ID del expediente asociado'),
    'descripcion': fields.String(),
})

historia_clinica_model = expediente.model('HistoriaClinica', {
    'id_expediente': fields.Integer(required=True, description='ID del expediente asociado'),
    'motivo_consulta': fields.String(),
})

antecedente_personal_model = expediente.model('AntecedentePersonal', {
    'id_expediente': fields.Integer(required=True, description='ID del expediente asociado'),
    'descripcion': fields.String(),
})

antecedente_familiar_model = expediente.model('AntecedenteFamiliar', {
    'id_expediente': fields.Integer(required=True, description='ID del expediente asociado'),
    'descripcion': fields.String(),
})


# Endpoints para Paciente (ya definidos)
@expediente.route('/paciente')
class PacienteList(Resource):
    @expediente.doc('list_pacientes')
    def get(self):
        pacientes = Paciente.query.all()
        return [paciente.as_dict() for paciente in pacientes], 200

    @expediente.doc('create_paciente')
    @expediente.expect(paciente_model)
    def post(self):
        data = request.get_json()

        # Verificar si el id_usuario existe
        id_usuario = data.get('id_usuario')
        if not User.query.filter_by(id_usuario=id_usuario).first():
            return {'message': 'Usuario no encontrado'}, 404

        paciente = Paciente.create_paciente(
            nombre=data.get('nombre', ''),
            nombre_segundo=data.get('nombre_segundo', ''),
            apellido_paterno=data.get('apellido_paterno', ''),
            apellido_materno=data.get('apellido_materno', ''),
            curp=data.get('curp', ''),
            telefono=data.get('telefono', ''),
            direccion=data.get('direccion', ''),
            estado=data.get('estado', ''),
            ciudad=data.get('ciudad', ''),
            estado_civil=data.get('estado_civil', ''),
            ocupacion=data.get('ocupacion', ''),
            id_usuario=id_usuario
        )
        return {'message': 'Paciente creado exitosamente', 'id_paciente': paciente.id_paciente}, 201

@expediente.route('/paciente/<int:id_paciente>')
class PacienteResource(Resource):
    @expediente.doc('get_paciente')
    def get(self, id_paciente):
        paciente = Paciente.get_paciente_by_id(id_paciente)
        if not paciente:
            return {'message': 'Paciente no encontrado'}, 404
        return paciente.as_dict(), 200

    @expediente.doc('update_paciente')
    @expediente.expect(paciente_model)
    def put(self, id_paciente):
        data = request.get_json()
        paciente = Paciente.get_paciente_by_id(id_paciente)
        if not paciente:
            return {'message': 'Paciente no encontrado'}, 404

        paciente.update_paciente(
            nombre=data.get('nombre'),
            nombre_segundo=data.get('nombre_segundo'),
            apellido_paterno=data.get('apellido_paterno'),
            apellido_materno=data.get('apellido_materno'),
            curp=data.get('curp'),
            telefono=data.get('telefono'),
            direccion=data.get('direccion'),
            estado=data.get('estado'),
            ciudad=data.get('ciudad'),
            estado_civil=data.get('estado_civil'),
            ocupacion=data.get('ocupacion')
        )
        return {'message': 'Paciente actualizado exitosamente'}, 200

    @expediente.doc('delete_paciente')
    def delete(self, id_paciente):
        paciente = Paciente.get_paciente_by_id(id_paciente)
        if not paciente:
            return {'message': 'Paciente no encontrado'}, 404
        paciente.delete_paciente()
        return {'message': 'Paciente eliminado exitosamente'}, 200


# Endpoints para Expediente
@expediente.route('/expediente')
class ExpedienteList(Resource):
    @expediente.doc('list_expedientes')
    def get(self):
        expedientes = Expediente.query.all()
        return [expediente.as_dict() for expediente in expedientes], 200

    @expediente.doc('create_expediente')
    @expediente.expect(expediente_model)
    def post(self):
        data = request.get_json()
        expediente = Expediente(
            id_paciente=data.get('id_paciente'),
            descripcion=data.get('descripcion', '')
        )
        db.session.add(expediente)
        db.session.commit()
        return {'message': 'Expediente creado exitosamente', 'id_expediente': expediente.id_expediente}, 201

@expediente.route('/expediente/<int:id_expediente>')
class ExpedienteResource(Resource):
    @expediente.doc('get_expediente')
    def get(self, id_expediente):
        expediente = Expediente.get_expediente_by_id(id_expediente)
        if not expediente:
            return {'message': 'Expediente no encontrado'}, 404
        return expediente.as_dict(), 200

    @expediente.doc('delete_expediente')
    def delete(self, id_expediente):
        expediente = Expediente.get_expediente_by_id(id_expediente)
        if not expediente:
            return {'message': 'Expediente no encontrado'}, 404
        db.session.delete(expediente)
        db.session.commit()
        return {'message': 'Expediente eliminado exitosamente'}, 200


# Endpoints para ModificacionExpediente
@expediente.route('/modificacion')
class ModificacionExpedienteList(Resource):
    @expediente.doc('list_modificaciones')
    def get(self):
        modificaciones = ModificacionExpediente.query.all()
        return [modificacion.as_dict() for modificacion in modificaciones], 200

    @expediente.doc('create_modificacion')
    @expediente.expect(modificacion_expediente_model)
    def post(self):
        data = request.get_json()
        modificacion = ModificacionExpediente.create_modificacion_expediente(
            id_expediente=data.get('id_expediente'),
            descripcion=data.get('descripcion', '')
        )
        return {'message': 'Modificación creada exitosamente', 'id_modificacion': modificacion.id_modificacion}, 201

@expediente.route('/modificacion/<int:id_modificacion>')
class ModificacionExpedienteResource(Resource):
    @expediente.doc('get_modificacion')
    def get(self, id_modificacion):
        modificacion = ModificacionExpediente.get_modificacion_by_id(id_modificacion)
        if not modificacion:
            return {'message': 'Modificación no encontrada'}, 404
        return modificacion.as_dict(), 200


# Endpoints para HistoriaClinica
@expediente.route('/historia_clinica')
class HistoriaClinicaList(Resource):
    @expediente.doc('list_historias_clinicas')
    def get(self):
        historias_clinicas = HistoriaClinica.query.all()
        return [historia_clinica.as_dict() for historia_clinica in historias_clinicas], 200

    @expediente.doc('create_historia_clinica')
    @expediente.expect(historia_clinica_model)
    def post(self):
        data = request.get_json()
        historia_clinica = HistoriaClinica(
            id_expediente=data.get('id_expediente'),
            motivo_consulta=data.get('motivo_consulta', '')
        )
        db.session.add(historia_clinica)
        db.session.commit()
        return {'message': 'Historia clínica creada exitosamente', 'id_historia_clinica': historia_clinica.id_historia_clinica}, 201

@expediente.route('/historia_clinica/<int:id_historia_clinica>')
class HistoriaClinicaResource(Resource):
    @expediente.doc('get_historia_clinica')
    def get(self, id_historia_clinica):
        historia_clinica = HistoriaClinica.get_historia_clinica_by_id(id_historia_clinica)
        if not historia_clinica:
            return {'message': 'Historia clínica no encontrada'}, 404
        return historia_clinica.as_dict(), 200


# Endpoints para AntecedentesPersonales
@expediente.route('/antecedente_personal')
class AntecedentePersonalList(Resource):
    @expediente.doc('list_antecedentes_personales')
    def get(self):
        antecedentes_personales = AntecedentesPersonales.query.all()
        return [antecedente.as_dict() for antecedente in antecedentes_personales], 200

    @expediente.doc('create_antecedente_personal')
    @expediente.expect(antecedente_personal_model)
    def post(self):
        data = request.get_json()
        antecedente_personal = AntecedentesPersonales(
            id_expediente=data.get('id_expediente'),
            descripcion=data.get('descripcion', '')
        )
        db.session.add(antecedente_personal)
        db.session.commit()
        return {'message': 'Antecedente personal creado exitosamente', 'id_antecedente_personal': antecedente_personal.id_antecedente_personal}, 201

@expediente.route('/antecedente_personal/<int:id_antecedente_personal>')
class AntecedentePersonalResource(Resource):
    @expediente.doc('get_antecedente_personal')
    def get(self, id_antecedente_personal):
        antecedente_personal = AntecedentesPersonales.query.filter_by(id_antecedente_personal=id_antecedente_personal).first()
        if not antecedente_personal:
            return {'message': 'Antecedente personal no encontrado'}, 404
        return antecedente_personal.as_dict(), 200


# Endpoints para AntecedentesFamiliares
@expediente.route('/antecedente_familiar')
class AntecedenteFamiliarList(Resource):
    @expediente.doc('list_antecedentes_familiares')
    def get(self):
        antecedentes_familiares = AntecedentesFamiliares.query.all()
        return [antecedente.as_dict() for antecedente in antecedentes_familiares], 200

    @expediente.doc('create_antecedente_familiar')
    @expediente.expect(antecedente_familiar_model)
    def post(self):
        data = request.get_json()
        antecedente_familiar = AntecedentesFamiliares(
            id_expediente=data.get('id_expediente'),
            descripcion=data.get('descripcion', '')
        )
        db.session.add(antecedente_familiar)
        db.session.commit()
        return {'message': 'Antecedente familiar creado exitosamente', 'id_antecedente_familiar': antecedente_familiar.id_antecedente_familiar}, 201

@expediente.route('/antecedente_familiar/<int:id_antecedente_familiar>')
class AntecedenteFamiliarResource(Resource):
    @expediente.doc('get_antecedente_familiar')
    def get(self, id_antecedente_familiar):
        antecedente_familiar = AntecedentesFamiliares.query.filter_by(id_antecedente_familiar=id_antecedente_familiar).first()
        if not antecedente_familiar:
            return {'message': 'Antecedente familiar no encontrado'}, 404
        return antecedente_familiar.as_dict(), 200

@expediente.route('/exportar_qr/<int:id_expediente>', methods=['GET'])
class ExportarQR(Resource):
    def get(self, id_expediente):
        expediente = Expediente.query.filter_by(id_expediente=id_expediente).first()
        if not expediente:
            return {'message': 'Expediente no encontrado'}, 404
        
        # Usar el token único existente o generar uno nuevo si no existe
        if not expediente.token_unico:
            expediente.token_unico = str(uuid.uuid4())
            db.session.commit()
        
        # Crear la URL pública del expediente
        url_publica = f"https://medibax.com/expediente/{expediente.token_unico}"
        
        # Generar el código QR basado en la URL
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url_publica)
        qr.make(fit=True)
        
        img = qr.make_image(fill='black', back_color='white')
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='expediente_qr.png')
    
def init_expediente_routes(api_instance):
    api_instance.add_namespace(expediente)