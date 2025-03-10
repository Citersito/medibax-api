from flask_restx import Namespace, Resource

api = Namespace('api', description='API operations')

@api.route('/index')
class Index(Resource):
    def get(self):
        return {'message': 'Hello, World!'}

def init_routes(api_instance):
    api_instance.add_namespace(api)
    