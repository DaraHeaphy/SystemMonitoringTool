# api.py
import requests
import time
from collections import deque
from .dtos import MetricsSnapshot

class MetricsAPI:
    def __init__(self, aggregator_url, api_key, retry_interval=30):

        self.aggregator_url = aggregator_url
        self.api_key = api_key
        self.headers = {'x-api-key': api_key}
        self.queue = deque()
        self.retry_interval = retry_interval

    def post_metrics(self, device_id, system_metrics, crypto_metrics):
        snapshot = MetricsSnapshot(device_id, system_metrics, crypto_metrics)
        payload = snapshot.to_dict()

        if not self._send_payload(payload):
            self.queue.append(payload)
            print("Payload added to queue for later retry:", payload)

    def _send_payload(self, payload):
        try:
            response = requests.post(
                self.aggregator_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            if response.ok:
                print("Successfully posted payload:", payload)
                return True
            else:
                print("Server error while posting payload:", response.status_code)
                return False
        except requests.RequestException as e:
            print("Request error:", e)
            return False

    def flush_queue(self):
        if not self.queue:
            return

        print("Attempting to flush", len(self.queue), "queued payloads.")
        for _ in range(len(self.queue)):
            payload = self.queue.popleft()
            if not self._send_payload(payload):
                self.queue.append(payload)
                break

    def run_flusher(self):
        while True:
            if self.queue:
                self.flush_queue()
            time.sleep(self.retry_interval)
