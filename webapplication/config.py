# config.py
import os

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    "mysql+pymysql://DaraHeaphy:Tarbert100@DaraHeaphy.mysql.pythonanywhere-services.com/DaraHeaphy$default"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True

API_KEYS = os.environ.get("API_KEYS", "954fffab-b3c3-49a1-89dd-3bbb55686a5d").split(',')