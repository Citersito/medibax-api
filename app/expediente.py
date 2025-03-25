from flask_restx import Namespace, Resource, fields
from flask import request
from .models import Paciente, Expediente, User

expediente = Namespace('expediente', description='Expediente operations')

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
    'usuario_id': fields.Integer(required=True, description='ID del usuario asociado'),
})

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

        # Verificar si el usuario_id existe
        usuario_id = data.get('usuario_id')
        if not User.query.filter_by(id=usuario_id).first():
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
            usuario_id=usuario_id
        )
        return {'message': 'Paciente creado exitosamente', 'id_paciente': paciente.id}, 201

@expediente.route('/paciente/<int:id>')
class PacienteResource(Resource):
    @expediente.doc('get_paciente')
    def get(self, id):
        paciente = Paciente.get_paciente_by_id(id)
        if not paciente:
            return {'message': 'Paciente no encontrado'}, 404
        return paciente.as_dict(), 200

    @expediente.doc('update_paciente')
    @expediente.expect(paciente_model)
    def put(self, id):
        data = request.get_json()
        paciente = Paciente.get_paciente_by_id(id)
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
    def delete(self, id):
        paciente = Paciente.get_paciente_by_id(id)
        if not paciente:
            return {'message': 'Paciente no encontrado'}, 404
        paciente.delete_paciente()
        return {'message': 'Paciente eliminado exitosamente'}, 200

def init_expediente_routes(api_instance):
    api_instance.add_namespace(expediente)