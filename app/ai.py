from flask_restx import Namespace, Resource, fields
from flask import request
from ai.disease_classifier import load_model_and_artifacts, predict_disease_api
import os

# Initialize namespace
ai_ns = Namespace('AI', description='Disease prediction operations', path='/api/ai')

try:
    # Load model artifacts
    model, scaler, label_encoder, feature_columns = load_model_and_artifacts()
    print("✅ Model artifacts loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model artifacts: {str(e)}")
    raise

# Load model artifacts once during startup
model, scaler, label_encoder, feature_columns = load_model_and_artifacts()

# Define API models for Swagger documentation
prediction_input = ai_ns.model('PredictionInput', {
    'age': fields.Integer(required=True, example=35),
    'sex': fields.String(required=True, enum=['M', 'F'], example='M'),
    'fever': fields.Integer(required=True, example=0, min=0, max=1),
    'sore_throat': fields.Integer(required=True, example=0, min=0, max=1),
    'cough': fields.Integer(required=True, example=0, min=0, max=1),
    'headache': fields.Integer(required=True, example=0, min=0, max=1),
    'fatigue': fields.Integer(required=True, example=0, min=0, max=1),
    'body_ache': fields.Integer(required=True, example=0, min=0, max=1),
    'runny_nose': fields.Integer(required=True, example=0, min=0, max=1),
    'congestion': fields.Integer(required=True, example=0, min=0, max=1),
    'shortness_of_breath': fields.Integer(required=True, example=0, min=0, max=1),
    'nausea': fields.Integer(required=True, example=0, min=0, max=1),
    'vomiting': fields.Integer(required=True, example=0, min=0, max=1),
    'diarrhea': fields.Integer(required=True, example=0, min=0, max=1),
    'chills': fields.Integer(required=True, example=0, min=0, max=1),
    'rash': fields.Integer(required=True, example=0, min=0, max=1),
    'chest_pain': fields.Integer(required=True, example=0, min=0, max=1),
    'dizziness': fields.Integer(required=True, example=0, min=0, max=1),
    'swollen_lymph_nodes': fields.Integer(required=True, example=0, min=0, max=1),
    'loss_of_appetite': fields.Integer(required=True, example=0, min=0, max=1),
    'joint_pain': fields.Integer(required=True, example=0, min=0, max=1),
    'abdominal_pain': fields.Integer(required=True, example=0, min=0, max=1),
    'ear_pain': fields.Integer(required=True, example=0, min=0, max=1),
    'eye_redness': fields.Integer(required=True, example=0, min=0, max=1),
    'loss_of_taste': fields.Integer(required=True, example=0, min=0, max=1),
    'loss_of_smell': fields.Integer(required=True, example=0, min=0, max=1),
    'wheezing': fields.Integer(required=True, example=0, min=0, max=1),
    'hoarse_voice': fields.Integer(required=True, example=0, min=0, max=1),
    'difficulty_swallowing': fields.Integer(required=True, example=0, min=0, max=1),
    'muscle_weakness': fields.Integer(required=True, example=0, min=0, max=1),
    'night_sweats': fields.Integer(required=True, example=0, min=0, max=1),
    'confusion': fields.Integer(required=True, example=0, min=0, max=1),
    'rapid_breathing': fields.Integer(required=True, example=0, min=0, max=1),
    'jaundice': fields.Integer(required=True, example=0, min=0, max=1),
    'itching': fields.Integer(required=True, example=0, min=0, max=1),
    'bruising': fields.Integer(required=True, example=0, min=0, max=1),
    'blood_in_stool': fields.Integer(required=True, example=0, min=0, max=1),
    'weight_loss': fields.Integer(required=True, example=0, min=0, max=1),
    'insomnia': fields.Integer(required=True, example=0, min=0, max=1),
    'sweating': fields.Integer(required=True, example=0, min=0, max=1),
    'symptom_duration_days': fields.Integer(required=True, example=3)
})

prediction_response = ai_ns.model('PredictionResponse', {
    'predicted_disease': fields.String,
    'confidence_scores': fields.Raw(example={'disease1': 0.95, 'disease2': 0.05})
})

@ai_ns.route('/predict')
class DiseasePredictor(Resource):
    @ai_ns.expect(prediction_input)
    @ai_ns.marshal_with(prediction_response)
    @ai_ns.doc(responses={
        400: 'Invalid input format',
        500: 'Internal server error'
    })
    def post(self):
        """
        Make disease prediction based on symptoms
        """
        try:
            data = request.json
            
            # Validate required features
            missing_features = [feat for feat in feature_columns if feat not in data]
            if missing_features:
                ai_ns.abort(400, f"Missing required features: {missing_features}")

            # Ensure proper data types
            try:
                data['sex'] = str(data['sex']).upper()
            except KeyError:
                ai_ns.abort(400, "Sex field is required")

            # Make prediction
            prediction = predict_disease_api(
                model=model,
                scaler=scaler,
                label_encoder=label_encoder,
                feature_columns=feature_columns,
                input_data=data
            )
            
            return prediction

        except ValueError as ve:
            ai_ns.abort(400, str(ve))
        except Exception as e:
            ai_ns.abort(500, str(e))

def init_ai_routes(api_instance):
    api_instance.add_namespace(ai_ns)