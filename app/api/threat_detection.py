from flask import jsonify, request
from app.api import bp
from app.services.threat_analyzer import ThreatAnalyzer
from app.utils.validators import validate_url

@bp.route('/analyze-url', methods=['POST'])
def analyze_url():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
        
    if not validate_url(url):
        return jsonify({'error': 'Invalid URL format'}), 400
    
    analyzer = ThreatAnalyzer()
    result = analyzer.analyze_url(url)
    
    return jsonify(result)

@bp.route('/scan-email', methods=['POST'])
def scan_email():
    data = request.get_json()
    email_content = data.get('content')
    
    if not email_content:
        return jsonify({'error': 'Email content is required'}), 400
    
    analyzer = ThreatAnalyzer()
    result = analyzer.scan_email(email_content)
    
    return jsonify(result)

@bp.route('/report-threat', methods=['POST'])
def report_threat():
    data = request.get_json()
    threat_type = data.get('type')
    threat_data = data.get('data')
    
    if not all([threat_type, threat_data]):
        return jsonify({'error': 'Threat type and data are required'}), 400
    
    analyzer = ThreatAnalyzer()
    result = analyzer.process_threat_report(threat_type, threat_data)
    
    return jsonify(result)
