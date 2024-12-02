from flask_sock import Sock
from ..services.packet_capture import packet_capture
import json
import threading
import time

sock = Sock()

@sock.route('/ws/packets')
def packet_socket(ws):
    """WebSocket handler for real-time packet updates."""
    last_packet_count = 0
    
    try:
        while True:
            # Get recent packets
            packets = packet_capture.get_recent_packets()
            current_count = len(packets)
            
            # If there are new packets, send them
            if current_count > last_packet_count:
                new_packets = packets[last_packet_count:]
                for packet in new_packets:
                    ws.send(json.dumps({
                        'time': packet['timestamp'],
                        'source': f"{packet['src']}:{packet['src_port']}" if packet['src_port'] else packet['src'],
                        'destination': f"{packet['dst']}:{packet['dst_port']}" if packet['dst_port'] else packet['dst'],
                        'protocol': packet['protocol'],
                        'length': packet['length'],
                        'info': packet['info']
                    }))
                last_packet_count = current_count
            
            # Sleep to prevent excessive CPU usage
            time.sleep(0.1)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
