import psutil
import time
from collections import deque

class NetworkMonitor:
    def __init__(self):
        self.history_size = 20
        self.speed_history = {
            'download': deque(maxlen=self.history_size),
            'upload': deque(maxlen=self.history_size),
            'timestamp': deque(maxlen=self.history_size)
        }
        self._last_io = psutil.net_io_counters()
        self._last_time = time.time()

    def get_network_stats(self):
        """Get current network statistics."""
        current_io = psutil.net_io_counters()
        current_time = time.time()
        
        time_delta = current_time - self._last_time
        
        # Calculate speeds
        download_speed = (current_io.bytes_recv - self._last_io.bytes_recv) / time_delta
        upload_speed = (current_io.bytes_sent - self._last_io.bytes_sent) / time_delta
        
        # Update history
        self.speed_history['download'].append(download_speed)
        self.speed_history['upload'].append(upload_speed)
        self.speed_history['timestamp'].append(current_time)
        
        # Update last values
        self._last_io = current_io
        self._last_time = current_time
        
        return {
            'download_speed': download_speed,
            'upload_speed': upload_speed,
            'active_connections': len(psutil.net_connections()),
            'history': {
                'download': list(self.speed_history['download']),
                'upload': list(self.speed_history['upload']),
                'timestamp': [time.strftime('%H:%M:%S', time.localtime(t)) 
                            for t in self.speed_history['timestamp']]
            }
        }

    def update_stats(self):
        """Update network statistics in real-time."""
        current_io = psutil.net_io_counters()
        current_time = time.time()
        
        if hasattr(self, '_last_io'):
            time_delta = current_time - self._last_time
            
            # Calculate speeds
            download_speed = (current_io.bytes_recv - self._last_io.bytes_recv) / time_delta
            upload_speed = (current_io.bytes_sent - self._last_io.bytes_sent) / time_delta
            
            # Update history
            self.speed_history['download'].append(download_speed)
            self.speed_history['upload'].append(upload_speed)
            self.speed_history['timestamp'].append(current_time)
        
        # Update last values
        self._last_io = current_io
        self._last_time = current_time

    def get_active_connections(self):
        """Get list of active network connections with detailed information."""
        connections = []
        connection_count = {
            'ESTABLISHED': 0,
            'LISTEN': 0,
            'TIME_WAIT': 0,
            'CLOSE_WAIT': 0,
            'OTHER': 0
        }
        
        process_connections = {}  # Track connections per process
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                # Count by status
                if conn.status in connection_count:
                    connection_count[conn.status] += 1
                else:
                    connection_count['OTHER'] += 1
                
                try:
                    if conn.pid:
                        process = psutil.Process(conn.pid)
                        process_name = process.name()
                        # Track connections per process
                        if process_name not in process_connections:
                            process_connections[process_name] = 0
                        process_connections[process_name] += 1
                        
                        connections.append({
                            'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                            'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                            'status': conn.status,
                            'pid': conn.pid,
                            'process_name': process_name,
                            'cpu_percent': process.cpu_percent(),
                            'memory_percent': process.memory_percent(),
                            'created_time': time.strftime('%Y-%m-%d %H:%M:%S', 
                                                        time.localtime(process.create_time()))
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                
        except (psutil.AccessDenied, psutil.Error) as e:
            print(f"Error accessing network connections: {e}")
        
        # Sort processes by connection count
        top_processes = sorted(process_connections.items(), 
                             key=lambda x: x[1], 
                             reverse=True)[:10]  # Top 10 processes
        
        return {
            'connections': connections,
            'summary': {
                'total': sum(connection_count.values()),
                'by_status': connection_count,
                'top_processes': [{'name': name, 'connections': count} 
                                for name, count in top_processes]
            }
        }

# Create a singleton instance
network_monitor = NetworkMonitor()
