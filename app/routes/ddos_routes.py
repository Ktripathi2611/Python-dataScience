from flask import Blueprint, jsonify, request
from app.modules.network_security.ddos_protection import DDoSProtection

ddos_bp = Blueprint('ddos', __name__)
ddos_protection = DDoSProtection()

@ddos_bp.route('/dashboard')
def dashboard():
    """Render DDoS protection dashboard."""
    return render_template('dashboard/ddos_protection.html')

@ddos_bp.route('/api/ddos/status')
def get_status():
    """Get current DDoS protection status."""
    return jsonify(ddos_protection.get_protection_status())

@ddos_bp.route('/api/ddos/settings', methods=['POST'])
def update_settings():
    """Update DDoS protection settings."""
    settings = request.get_json()
    ddos_protection.update_thresholds(settings)
    return jsonify({'status': 'success'})

@ddos_bp.before_request
def check_request():
    """Check each request for potential DDoS attacks."""
    ip = request.remote_addr
    if not ddos_protection.check_connection(ip):
        return jsonify({'error': 'Too many requests'}), 429
