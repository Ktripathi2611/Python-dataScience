from flask import jsonify, request
from app.api import bp
from app.services.deep_fake_detector import DeepFakeDetector
from app.utils.file_handlers import save_uploaded_file, allowed_file

@bp.route('/analyze-media', methods=['POST'])
def analyze_media():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not supported'}), 400
    
    file_path = save_uploaded_file(file)
    detector = DeepFakeDetector()
    result = detector.analyze_media(file_path)
    
    return jsonify(result)

@bp.route('/analyze-video', methods=['POST'])
def analyze_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
        
    video = request.files['video']
    if video.filename == '':
        return jsonify({'error': 'No video selected'}), 400
        
    if not allowed_file(video.filename, ['mp4', 'avi', 'mov']):
        return jsonify({'error': 'Video format not supported'}), 400
    
    file_path = save_uploaded_file(video)
    detector = DeepFakeDetector()
    result = detector.analyze_video(file_path)
    
    return jsonify(result)

@bp.route('/analyze-audio', methods=['POST'])
def analyze_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
        
    audio = request.files['audio']
    if audio.filename == '':
        return jsonify({'error': 'No audio selected'}), 400
        
    if not allowed_file(audio.filename, ['mp3', 'wav']):
        return jsonify({'error': 'Audio format not supported'}), 400
    
    file_path = save_uploaded_file(audio)
    detector = DeepFakeDetector()
    result = detector.analyze_audio(file_path)
    
    return jsonify(result)
