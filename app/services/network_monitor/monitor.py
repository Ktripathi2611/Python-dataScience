import psutil
import time
from datetime import datetime

class NetworkMonitor:
    def __init__(self):
        self.previous_stats = None
        self.current_stats = None

    def get_network_stats(self):
        # Get network statistics
        stats = psutil.net_io_counters()
        current_time = datetime.now().strftime("%H:%M:%S")
        
        network_data = {
            "timestamp": current_time,
            "bytes_sent": stats.bytes_sent,
            "bytes_recv": stats.bytes_recv,
            "packets_sent": stats.packets_sent,
            "packets_recv": stats.packets_recv,
            "connections": len(psutil.net_connections()),
        }

        # Calculate speeds if previous stats exist
        if self.previous_stats:
            time_diff = time.time() - self.previous_stats['time']
            network_data.update({
                "upload_speed": (stats.bytes_sent - self.previous_stats['bytes_sent']) / time_diff,
                "download_speed": (stats.bytes_recv - self.previous_stats['bytes_recv']) / time_diff
            })
        else:
            network_data.update({
                "upload_speed": 0,
                "download_speed": 0
            })

        # Update previous stats
        self.previous_stats = {
            'time': time.time(),
            'bytes_sent': stats.bytes_sent,
            'bytes_recv': stats.bytes_recv
        }

        return network_data

    def get_active_connections(self):
        connections = []
        for conn in psutil.net_connections():
            if conn.status == 'ESTABLISHED':
                try:
                    process = psutil.Process(conn.pid) if conn.pid else None
                    connections.append({
                        'local_address': f"{conn.laddr.ip}:{conn.laddr.port}",
                        'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                        'status': conn.status,
                        'process': process.name() if process else "Unknown",
                        'pid': conn.pid if conn.pid else "N/A"
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        return connections[:10]  # Return only top 10 connections

network_monitor = NetworkMonitor()
