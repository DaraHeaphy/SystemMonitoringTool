import os

AGGREGATOR_API_URL = os.environ.get("AGGREGATOR_API_URL", "https://DaraHeaphy.pythonanywhere.com/api/aggregator")
COMMAND_API_URL = os.environ.get("COMMAND_API_URL", "https://DaraHeaphy.pythonanywhere.com/get-command")
DEVICE_API_URL = os.environ.get("DEVICE_API_URL", "https://daraheaphy.pythonanywhere.com/api/device")

API_KEY = os.environ.get("API_KEY", "954fffab-b3c3-49a1-89dd-3bbb55686a5d")

HEADERS = {'x-api-key': API_KEY}

COLLECTION_INTERVAL = int(os.environ.get("COLLECTION_INTERVAL", 30))
RETRY_INTERVAL = int(os.environ.get("RETRY_INTERVAL", 30))