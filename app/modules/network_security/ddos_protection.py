import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Optional
import threading
import logging
from datetime import datetime, timedelta

@dataclass
class ConnectionStats:
    ip_address: str
    request_count: int
    first_request: float
    last_request: float
    blocked_until: Optional[float] = None

class DDoSProtection:
    def __init__(self):
        self.connection_tracker = defaultdict(lambda: deque(maxlen=1000))
        self.ip_stats: Dict[str, ConnectionStats] = {}
        self.blocked_ips: Dict[str, float] = {}
        self.thresholds = {
            'requests_per_minute': 100,  # Max requests per minute
            'burst_limit': 20,           # Max burst requests
            'burst_time': 5,             # Time window for burst (seconds)
            'block_duration': 300        # Block duration in seconds (5 minutes)
        }
        self.setup_logging()
        self.start_cleanup_thread()

    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ddos_protection.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def start_cleanup_thread(self):
        """Start background thread for cleaning up old records."""
        def cleanup():
            while True:
                self._cleanup_old_records()
                time.sleep(60)  # Run cleanup every minute

        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()

    def check_connection(self, ip_address: str) -> bool:
        """
        Check if a connection should be allowed.
        Returns True if connection is allowed, False if it should be blocked.
        """
        current_time = time.time()

        # Check if IP is blocked
        if self._is_blocked(ip_address):
            self.logger.warning(f"Blocked connection attempt from {ip_address}")
            return False

        # Record the connection
        self.connection_tracker[ip_address].append(current_time)
        
        # Update IP stats
        self._update_ip_stats(ip_address, current_time)
        
        # Check for DDoS patterns
        if self._check_ddos_patterns(ip_address):
            self._block_ip(ip_address)
            return False

        return True

    def _is_blocked(self, ip_address: str) -> bool:
        """Check if an IP is currently blocked."""
        if ip_address in self.blocked_ips:
            if time.time() < self.blocked_ips[ip_address]:
                return True
            else:
                del self.blocked_ips[ip_address]
        return False

    def _update_ip_stats(self, ip_address: str, current_time: float):
        """Update statistics for an IP address."""
        if ip_address not in self.ip_stats:
            self.ip_stats[ip_address] = ConnectionStats(
                ip_address=ip_address,
                request_count=1,
                first_request=current_time,
                last_request=current_time
            )
        else:
            stats = self.ip_stats[ip_address]
            stats.request_count += 1
            stats.last_request = current_time

    def _check_ddos_patterns(self, ip_address: str) -> bool:
        """
        Check for DDoS attack patterns.
        Returns True if DDoS pattern is detected.
        """
        current_time = time.time()
        recent_requests = self.connection_tracker[ip_address]
        
        # Check request rate
        one_minute_ago = current_time - 60
        requests_last_minute = sum(1 for t in recent_requests if t > one_minute_ago)
        if requests_last_minute > self.thresholds['requests_per_minute']:
            self.logger.warning(f"Rate limit exceeded for {ip_address}: {requests_last_minute} requests/minute")
            return True

        # Check burst pattern
        burst_window = current_time - self.thresholds['burst_time']
        recent_burst = sum(1 for t in recent_requests if t > burst_window)
        if recent_burst > self.thresholds['burst_limit']:
            self.logger.warning(f"Burst limit exceeded for {ip_address}: {recent_burst} requests in {self.thresholds['burst_time']}s")
            return True

        return False

    def _block_ip(self, ip_address: str):
        """Block an IP address for the configured duration."""
        block_until = time.time() + self.thresholds['block_duration']
        self.blocked_ips[ip_address] = block_until
        self.logger.warning(f"Blocking IP {ip_address} until {datetime.fromtimestamp(block_until)}")

    def _cleanup_old_records(self):
        """Clean up old records and expired blocks."""
        current_time = time.time()
        
        # Clean up old connection records
        for ip in list(self.connection_tracker.keys()):
            self.connection_tracker[ip] = deque(
                (t for t in self.connection_tracker[ip] if current_time - t < 3600),
                maxlen=1000
            )
            if not self.connection_tracker[ip]:
                del self.connection_tracker[ip]

        # Clean up old IP stats
        for ip in list(self.ip_stats.keys()):
            if current_time - self.ip_stats[ip].last_request > 3600:
                del self.ip_stats[ip]

        # Clean up expired blocks
        for ip in list(self.blocked_ips.keys()):
            if current_time > self.blocked_ips[ip]:
                del self.blocked_ips[ip]

    def get_protection_status(self) -> Dict:
        """Get current DDoS protection status."""
        current_time = time.time()
        return {
            'active_connections': sum(len(conns) for conns in self.connection_tracker.values()),
            'tracked_ips': len(self.ip_stats),
            'blocked_ips': {
                ip: {
                    'blocked_until': datetime.fromtimestamp(until).isoformat(),
                    'remaining_seconds': int(until - current_time)
                }
                for ip, until in self.blocked_ips.items()
            },
            'thresholds': self.thresholds,
            'top_ips': self._get_top_ips(5)
        }

    def _get_top_ips(self, limit: int) -> List[Dict]:
        """Get top IPs by request count."""
        return sorted(
            [
                {
                    'ip': stats.ip_address,
                    'request_count': stats.request_count,
                    'first_request': datetime.fromtimestamp(stats.first_request).isoformat(),
                    'last_request': datetime.fromtimestamp(stats.last_request).isoformat()
                }
                for stats in self.ip_stats.values()
            ],
            key=lambda x: x['request_count'],
            reverse=True
        )[:limit]

    def update_thresholds(self, new_thresholds: Dict):
        """Update protection thresholds."""
        valid_keys = set(self.thresholds.keys())
        for key, value in new_thresholds.items():
            if key in valid_keys and isinstance(value, (int, float)) and value > 0:
                self.thresholds[key] = value
                self.logger.info(f"Updated {key} threshold to {value}")
