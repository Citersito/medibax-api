from flask_restx import Namespace, Resource

ai_model = Namespace('AI', description='AI operations')

# expediente_model = expediente_model('Expediente', {
#     'email': fields.String(required=True, description='Email'),
#     'password': fields.String(required=True, description='Password'),
# })

@ai_model.route('/')
class AIModel(Resource):
    def get(self):
        return {'message': 'AI retrieved'}

def init_ai_routes(api_instance):
    api_instance.add_namespace(ai_model)