import psutil
import requests
import time

def gather_local_metrics():
    battery = psutil.sensors_battery()
    battery_level = battery.percent if battery else None

    ram_usage = psutil.virtual_memory().percent

    net_io = psutil.net_io_counters()
    network_sent = net_io.bytes_sent
    network_recv = net_io.bytes_recv

    return {
        "battery_level": battery_level,
        "ram_usage": ram_usage,
        "network_sent": network_sent,
        "network_recv": network_recv
    }