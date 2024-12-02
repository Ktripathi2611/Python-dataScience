from flask import Blueprint, jsonify
from ..services.packet_capture import packet_capture

packet = Blueprint('packet', __name__)

@packet.route('/api/packets/recent')
def get_recent_packets():
    """Get recent network packets."""
    return jsonify(packet_capture.get_recent_packets())

@packet.route('/api/packets/stats')
def get_packet_stats():
    """Get packet statistics."""
    return jsonify(packet_capture.get_statistics())

@packet.route('/api/packets/start', methods=['POST'])
def start_capture():
    """Start packet capture."""
    packet_capture.start_capture()
    return jsonify({"status": "success", "message": "Packet capture started"})

@packet.route('/api/packets/stop', methods=['POST'])
def stop_capture():
    """Stop packet capture."""
    packet_capture.stop_capture()
    return jsonify({"status": "success", "message": "Packet capture stopped"})

@packet.route('/api/packets/clear', methods=['POST'])
def clear_capture():
    """Clear captured packets."""
    packet_capture.clear_capture()
    return jsonify({"status": "success", "message": "Packet capture cleared"})
