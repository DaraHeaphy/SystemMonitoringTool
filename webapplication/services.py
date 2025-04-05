# services.py
from webapplication.models import Metric, Device

def reconstruct_metric(metric):

    values = {mv.attribute_name: mv.attribute_value for mv in metric.values}
    values['timestamp'] = metric.timestamp
    return values

def get_latest_system_metrics(limit=20):

    system_metrics = Metric.query.filter_by(metric_type='system') \
        .order_by(Metric.timestamp.desc()).limit(limit).all()
    system_metrics.reverse()  # so oldest is first
    return [reconstruct_metric(m) for m in system_metrics]

def get_crypto_metrics(coin_type, limit=20):

    metric_type = f"crypto_{coin_type}"
    metrics = Metric.query.filter_by(metric_type=metric_type) \
        .order_by(Metric.timestamp.desc()).limit(limit).all()
    metrics.reverse()
    return [reconstruct_metric(m) for m in metrics]

def get_device_list():

    devices = Device.query.order_by(Device.name).all()
    return [{"id": d.id, "name": d.name} for d in devices]