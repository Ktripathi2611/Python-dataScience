from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP
from datetime import datetime
import threading
import queue
import time
import json
from collections import deque

class PacketCaptureService:
    def __init__(self, max_packets=1000):
        self.packet_queue = queue.Queue()
        self.packet_history = deque(maxlen=max_packets)
        self.running = False
        self.capture_thread = None
        self.analysis_thread = None
        self.protocol_stats = {
            'TCP': 0, 'UDP': 0, 'ICMP': 0, 'ARP': 0, 'Other': 0
        }
        self.port_stats = {}
        self.ip_stats = {}
        self._lock = threading.Lock()

    def start_capture(self):
        """Start packet capture in a separate thread."""
        if not self.running:
            self.running = True
            self.capture_thread = threading.Thread(target=self._capture_packets, daemon=True)
            self.analysis_thread = threading.Thread(target=self._analyze_packets, daemon=True)
            self.capture_thread.start()
            self.analysis_thread.start()

    def stop_capture(self):
        """Stop packet capture."""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join()
        if self.analysis_thread:
            self.analysis_thread.join()

    def _capture_packets(self):
        """Capture packets using scapy."""
        try:
            sniff(prn=self._packet_callback, store=False, 
                  stop_filter=lambda _: not self.running)
        except Exception as e:
            print(f"Error in packet capture: {e}")
            self.running = False

    def _packet_callback(self, packet):
        """Callback function for each captured packet."""
        try:
            self.packet_queue.put(packet)
        except Exception as e:
            print(f"Error in packet callback: {e}")

    def _analyze_packets(self):
        """Analyze packets from the queue."""
        while self.running:
            try:
                if not self.packet_queue.empty():
                    packet = self.packet_queue.get(timeout=1)
                    packet_info = self._extract_packet_info(packet)
                    if packet_info:
                        with self._lock:
                            self.packet_history.append(packet_info)
                            self._update_statistics(packet_info)
            except queue.Empty:
                time.sleep(0.1)
            except Exception as e:
                print(f"Error analyzing packet: {e}")

    def _extract_packet_info(self, packet):
        """Extract relevant information from a packet."""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            packet_info = {
                'timestamp': timestamp,
                'protocol': 'Unknown',
                'length': len(packet),
                'src': '',
                'dst': '',
                'src_port': '',
                'dst_port': '',
                'flags': [],
                'info': ''
            }

            # IP Layer
            if IP in packet:
                packet_info['src'] = packet[IP].src
                packet_info['dst'] = packet[IP].dst
                
                # TCP Layer
                if TCP in packet:
                    packet_info['protocol'] = 'TCP'
                    packet_info['src_port'] = packet[TCP].sport
                    packet_info['dst_port'] = packet[TCP].dport
                    packet_info['flags'] = self._get_tcp_flags(packet[TCP])
                    packet_info['info'] = f"TCP {packet_info['src_port']} → {packet_info['dst_port']}"
                
                # UDP Layer
                elif UDP in packet:
                    packet_info['protocol'] = 'UDP'
                    packet_info['src_port'] = packet[UDP].sport
                    packet_info['dst_port'] = packet[UDP].dport
                    packet_info['info'] = f"UDP {packet_info['src_port']} → {packet_info['dst_port']}"
                
                # ICMP Layer
                elif ICMP in packet:
                    packet_info['protocol'] = 'ICMP'
                    packet_info['info'] = f"ICMP {packet[ICMP].type}"

            # ARP Layer
            elif ARP in packet:
                packet_info['protocol'] = 'ARP'
                packet_info['src'] = packet[ARP].psrc
                packet_info['dst'] = packet[ARP].pdst
                packet_info['info'] = f"Who has {packet[ARP].pdst}? Tell {packet[ARP].psrc}"

            return packet_info
        except Exception as e:
            print(f"Error extracting packet info: {e}")
            return None

    def _get_tcp_flags(self, tcp):
        """Get TCP flags as a list of strings."""
        flags = []
        if tcp.flags.S: flags.append('SYN')
        if tcp.flags.A: flags.append('ACK')
        if tcp.flags.F: flags.append('FIN')
        if tcp.flags.R: flags.append('RST')
        if tcp.flags.P: flags.append('PSH')
        if tcp.flags.U: flags.append('URG')
        return flags

    def _update_statistics(self, packet_info):
        """Update protocol, port, and IP statistics."""
        # Update protocol stats
        self.protocol_stats[packet_info['protocol']] = \
            self.protocol_stats.get(packet_info['protocol'], 0) + 1

        # Update port stats
        if packet_info['src_port']:
            self.port_stats[packet_info['src_port']] = \
                self.port_stats.get(packet_info['src_port'], 0) + 1
        if packet_info['dst_port']:
            self.port_stats[packet_info['dst_port']] = \
                self.port_stats.get(packet_info['dst_port'], 0) + 1

        # Update IP stats
        if packet_info['src']:
            self.ip_stats[packet_info['src']] = \
                self.ip_stats.get(packet_info['src'], 0) + 1
        if packet_info['dst']:
            self.ip_stats[packet_info['dst']] = \
                self.ip_stats.get(packet_info['dst'], 0) + 1

    def get_recent_packets(self, limit=100):
        """Get the most recent packets."""
        with self._lock:
            return list(self.packet_history)[-limit:]

    def get_statistics(self):
        """Get current statistics."""
        with self._lock:
            return {
                'protocols': dict(self.protocol_stats),
                'top_ports': dict(sorted(self.port_stats.items(), 
                                      key=lambda x: x[1], 
                                      reverse=True)[:10]),
                'top_ips': dict(sorted(self.ip_stats.items(), 
                                    key=lambda x: x[1], 
                                    reverse=True)[:10])
            }

    def clear_capture(self):
        """Clear all captured packets and statistics."""
        with self._lock:
            self.packet_history.clear()
            self.protocol_stats = {'TCP': 0, 'UDP': 0, 'ICMP': 0, 'ARP': 0, 'Other': 0}
            self.port_stats.clear()
            self.ip_stats.clear()

# Create singleton instance
packet_capture = PacketCaptureService()
