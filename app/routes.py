from flask import render_template, jsonify, request
from app import app
import re
import requests
from datetime import datetime

def is_valid_url(url):
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/api/scan-url', methods=['POST'])
def scan_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'status': 'error', 'message': 'No URL provided'}), 400
    
    url = data['url']
    if not is_valid_url(url):
        return jsonify({'status': 'error', 'message': 'Invalid URL format'}), 400

    # Basic security checks
    security_status = {
        'malicious': False,
        'suspicious_patterns': [],
        'ssl_secure': url.startswith('https'),
        'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    try:
        # Check if website is accessible
        response = requests.head(url, timeout=5)
        security_status['status_code'] = response.status_code
        security_status['accessible'] = True
    except requests.RequestException:
        security_status['accessible'] = False
        security_status['error'] = 'Website not accessible'

    return jsonify({
        'status': 'success',
        'message': 'URL scan completed',
        'results': security_status
    })

@app.route('/api/scan-image', methods=['POST'])
def scan_image():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image file provided'}), 400
    
    image = request.files['image']
    if image.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return jsonify({'status': 'error', 'message': 'Invalid file format'}), 400

    # Basic image analysis (placeholder for deep fake detection)
    analysis_result = {
        'filename': image.filename,
        'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'file_size': len(image.read()),
        'preliminary_check': 'No obvious manipulation detected',
        'confidence_score': 0.95,  # Placeholder score
        'scan_status': 'completed'
    }

    return jsonify({
        'status': 'success',
        'message': 'Image scan completed',
        'results': analysis_result
    })

@app.route('/api/security-status')
def security_status():
    # Simulated security status
    return jsonify({
        'status': 'protected',
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'stats': {
            'threats_blocked': 127,
            'deep_fakes_detected': 15,
            'suspicious_urls_blocked': 89,
            'safe_browsing_hours': 248
        },
        'components': {
            'threat_detection': {
                'status': 'active',
                'last_update': '2 minutes ago'
            },
            'deep_fake_detection': {
                'status': 'enabled',
                'last_scan': '15 minutes ago'
            },
            'ai_learning': {
                'status': 'active',
                'models_updated': '1 hour ago'
            }
        }
    })

# Recent activity endpoint
@app.route('/api/recent-activity')
def recent_activity():
    # Simulated recent activity
    return jsonify({
        'activities': [
            {
                'type': 'threat_blocked',
                'description': 'Phishing attempt blocked',
                'time': '2m ago',
                'severity': 'high'
            },
            {
                'type': 'deep_fake_detected',
                'description': 'Deep fake image detected',
                'time': '15m ago',
                'severity': 'medium'
            },
            {
                'type': 'scan_completed',
                'description': 'Security scan completed',
                'time': '1h ago',
                'severity': 'low'
            }
        ]
    })
