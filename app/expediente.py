from flask_restx import Namespace, Resource

expediente = Namespace('expediente', description='Expediente operations')

# expediente_model = expediente_model('Expediente', {
#     'email': fields.String(required=True, description='Email'),
#     'password': fields.String(required=True, description='Password'),
# })


@expediente.route('/')
class Expediente(Resource):
    def get(self):
        return {'message': 'Expediente retrieved'}

@expediente.route('/create')
class CreateExpediente(Resource):
    def post(self):
        return {'message': 'Expediente created'}

def init_expediente_routes(api_instance):
    api_instance.add_namespace(expediente)
    