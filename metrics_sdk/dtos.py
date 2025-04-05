# dtos.py
# metrics_sdk/dtos.py
import time

class MetricsSnapshot:
    def __init__(self, device_id, system_metrics, crypto_metrics):
        self.device_id = device_id
        self.system_metrics = system_metrics
        self.crypto_metrics = crypto_metrics
        self.timestamp = time.time()
    
    def to_dict(self):
        return {
            "device_id": self.device_id,
            "system": self.system_metrics,
            "crypto": self.crypto_metrics,
            "timestamp": self.timestamp
        }
