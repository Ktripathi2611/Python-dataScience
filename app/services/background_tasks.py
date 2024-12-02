import threading
import time
from ..utils.network_monitor import network_monitor
from .packet_capture import packet_capture

class BackgroundTaskManager:
    def __init__(self):
        self.tasks = []
        self.running = False
        self._lock = threading.Lock()

    def start(self):
        if not self.running:
            self.running = True
            self._start_network_monitoring()
            self._start_packet_capture()

    def stop(self):
        self.running = False
        packet_capture.stop_capture()
        for task in self.tasks:
            if task.is_alive():
                task.join()

    def _start_network_monitoring(self):
        def run_monitoring():
            while self.running:
                with self._lock:
                    network_monitor.update_stats()
                time.sleep(1)  # Update every second

        monitor_thread = threading.Thread(target=run_monitoring, daemon=True)
        monitor_thread.start()
        self.tasks.append(monitor_thread)

    def _start_packet_capture(self):
        packet_capture.start_capture()

# Create singleton instance
task_manager = BackgroundTaskManager()
