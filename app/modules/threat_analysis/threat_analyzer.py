import psutil
import time
from collections import defaultdict
import numpy as np
from datetime import datetime, timedelta

class ThreatAnalyzer:
    def __init__(self):
        self.connection_history = defaultdict(list)
        self.threat_patterns = {
            'port_scan': {'threshold': 10, 'time_window': 60},  # 10 ports in 60 seconds
            'ddos': {'threshold': 100, 'time_window': 60},      # 100 connections in 60 seconds
            'brute_force': {'threshold': 5, 'time_window': 30}  # 5 failed attempts in 30 seconds
        }
        self.known_malicious_ips = set()
        self.suspicious_activities = []
    
    def analyze_network_activity(self, connections):
        """Analyze network connections for suspicious activity."""
        current_time = time.time()
        threats = []
        
        # Group connections by remote IP
        ip_connections = defaultdict(list)
        for conn in connections:
            if conn.raddr:
                ip_connections[conn.raddr.ip].append(conn)
        
        # Analyze each IP's activity
        for ip, conns in ip_connections.items():
            # Check for port scanning
            if self._detect_port_scan(ip, conns):
                threats.append({
                    'type': 'port_scan',
                    'ip': ip,
                    'severity': 'high',
                    'timestamp': current_time
                })
            
            # Check for DDoS patterns
            if self._detect_ddos(ip, conns):
                threats.append({
                    'type': 'ddos',
                    'ip': ip,
                    'severity': 'critical',
                    'timestamp': current_time
                })
            
            # Check for brute force attempts
            if self._detect_brute_force(ip, conns):
                threats.append({
                    'type': 'brute_force',
                    'ip': ip,
                    'severity': 'high',
                    'timestamp': current_time
                })
        
        return threats
    
    def _detect_port_scan(self, ip, connections):
        """Detect potential port scanning activity."""
        recent_ports = set()
        start_time = time.time() - self.threat_patterns['port_scan']['time_window']
        
        for conn in connections:
            if conn.raddr and conn.raddr.ip == ip and conn.status == 'SYN_SENT':
                if conn.laddr.port not in recent_ports:
                    recent_ports.add(conn.laddr.port)
        
        return len(recent_ports) >= self.threat_patterns['port_scan']['threshold']
    
    def _detect_ddos(self, ip, connections):
        """Detect potential DDoS attacks."""
        recent_connections = [
            conn for conn in connections
            if time.time() - conn.create_time < self.threat_patterns['ddos']['time_window']
        ]
        
        return len(recent_connections) >= self.threat_patterns['ddos']['threshold']
    
    def _detect_brute_force(self, ip, connections):
        """Detect potential brute force attempts."""
        failed_attempts = [
            conn for conn in connections
            if conn.status == 'CLOSE' and 
            time.time() - conn.create_time < self.threat_patterns['brute_force']['time_window']
        ]
        
        return len(failed_attempts) >= self.threat_patterns['brute_force']['threshold']
    
    def analyze_process_behavior(self, process):
        """Analyze process behavior for suspicious activity."""
        suspicious = []
        
        try:
            # Check CPU usage
            if process.cpu_percent() > 80:
                suspicious.append({
                    'type': 'high_cpu_usage',
                    'severity': 'medium',
                    'details': f"Process using {process.cpu_percent()}% CPU"
                })
            
            # Check memory usage
            if process.memory_percent() > 50:
                suspicious.append({
                    'type': 'high_memory_usage',
                    'severity': 'medium',
                    'details': f"Process using {process.memory_percent()}% memory"
                })
            
            # Check file operations
            open_files = process.open_files()
            if len(open_files) > 100:
                suspicious.append({
                    'type': 'excessive_file_operations',
                    'severity': 'high',
                    'details': f"Process has {len(open_files)} open files"
                })
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return suspicious
    
    def get_threat_summary(self):
        """Get a summary of current threats."""
        return {
            'total_threats': len(self.suspicious_activities),
            'by_severity': {
                'critical': sum(1 for t in self.suspicious_activities if t['severity'] == 'critical'),
                'high': sum(1 for t in self.suspicious_activities if t['severity'] == 'high'),
                'medium': sum(1 for t in self.suspicious_activities if t['severity'] == 'medium'),
                'low': sum(1 for t in self.suspicious_activities if t['severity'] == 'low')
            },
            'recent_threats': sorted(
                self.suspicious_activities,
                key=lambda x: x['timestamp'],
                reverse=True
            )[:10]
        }
    
    def update_malicious_ips(self, ip_list):
        """Update the list of known malicious IPs."""
        self.known_malicious_ips.update(ip_list)
