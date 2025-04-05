# app/models.py
import uuid
from datetime import datetime
from . import db

class Device(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Device {self.name}>"

class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(36), db.ForeignKey('device.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    metric_type = db.Column(db.String(50), nullable=False)

    values = db.relationship('MetricValue', backref='metric', cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<Metric {self.metric_type} {self.timestamp}>"

class MetricValue(db.Model):
    metric_id = db.Column(db.Integer, db.ForeignKey('metric.id'), primary_key=True)
    attribute_name = db.Column(db.String(50), primary_key=True)
    attribute_value = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<MetricValue {self.attribute_name}: {self.attribute_value}>"

class CommandQueue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

