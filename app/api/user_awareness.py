from flask import jsonify, request
from app.api import bp
from app.services.awareness_trainer import AwarenessTrainer

@bp.route('/get-security-tips', methods=['GET'])
def get_security_tips():
    category = request.args.get('category', 'general')
    trainer = AwarenessTrainer()
    tips = trainer.get_security_tips(category)
    return jsonify(tips)

@bp.route('/get-tutorial', methods=['GET'])
def get_tutorial():
    topic = request.args.get('topic')
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400
    
    trainer = AwarenessTrainer()
    tutorial = trainer.get_tutorial(topic)
    return jsonify(tutorial)

@bp.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    data = request.get_json()
    user_id = data.get('user_id')
    quiz_id = data.get('quiz_id')
    answers = data.get('answers')
    
    if not all([user_id, quiz_id, answers]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    trainer = AwarenessTrainer()
    result = trainer.evaluate_quiz(user_id, quiz_id, answers)
    return jsonify(result)

@bp.route('/get-response-guide', methods=['GET'])
def get_response_guide():
    incident_type = request.args.get('type')
    if not incident_type:
        return jsonify({'error': 'Incident type is required'}), 400
    
    trainer = AwarenessTrainer()
    guide = trainer.get_response_guide(incident_type)
    return jsonify(guide)
