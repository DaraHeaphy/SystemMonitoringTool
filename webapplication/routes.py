from flask import request, jsonify, render_template, current_app
from webapplication import app, db
from webapplication.models import Metric, MetricValue, CommandQueue, Device
from webapplication.services import (
    reconstruct_metric,
    get_latest_system_metrics,
    get_crypto_metrics,
    get_device_list
)
import uuid

@app.route('/')
def dashboard():
    # Get reconstructed system metrics data
    system_data = get_latest_system_metrics(limit=20)
    network_labels = [m['timestamp'].strftime('%H:%M:%S') for m in system_data]
    network_sent_data = [m.get('network_sent', 0) for m in system_data]
    network_recv_data = [m.get('network_recv', 0) for m in system_data]

    # Get crypto metrics for Bitcoin and Ethereum
    # Note: We use the keyword 'coin_type' to match the signature in services.py.
    bitcoin_data = get_crypto_metrics(coin_type="bitcoin", limit=20)
    bitcoin_labels = [m['timestamp'].strftime('%H:%M:%S') for m in bitcoin_data]
    bitcoin_prices = [round(m.get('price_usd', 0), 2) for m in bitcoin_data]
    bitcoin_market_caps = [m.get('market_cap_usd', 0) for m in bitcoin_data]
    bitcoin_change = [m.get('price_change_percentage_24h', 0) for m in bitcoin_data]

    ethereum_data = get_crypto_metrics(coin_type="ethereum", limit=20)
    ethereum_labels = [m['timestamp'].strftime('%H:%M:%S') for m in ethereum_data]
    ethereum_prices = [round(m.get('price_usd', 0), 2) for m in ethereum_data]
    ethereum_market_caps = [m.get('market_cap_usd', 0) for m in ethereum_data]
    ethereum_change = [m.get('price_change_percentage_24h', 0) for m in ethereum_data]

    # For charts that compare both coins, assume Bitcoin's labels (aligned timestamps)
    crypto_labels = bitcoin_labels

    # Get the list of devices
    device_list = get_device_list()

    return render_template('dashboard.html',
                           network_labels=network_labels,
                           network_sent_data=network_sent_data,
                           network_recv_data=network_recv_data,
                           bitcoin_labels=bitcoin_labels,
                           bitcoin_prices=bitcoin_prices,
                           bitcoin_market_caps=bitcoin_market_caps,
                           bitcoin_change=bitcoin_change,
                           ethereum_labels=ethereum_labels,
                           ethereum_prices=ethereum_prices,
                           ethereum_market_caps=ethereum_market_caps,
                           ethereum_change=ethereum_change,
                           crypto_labels=crypto_labels,
                           device_list=device_list)

@app.route('/history', methods=['GET'])
def history():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    system_pagination = Metric.query.filter_by(metric_type='system') \
        .order_by(Metric.timestamp.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)
    system_metrics = [reconstruct_metric(m) for m in system_pagination.items]

    bitcoin_pagination = Metric.query.filter_by(metric_type='crypto_bitcoin') \
        .order_by(Metric.timestamp.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)
    bitcoin_metrics = [reconstruct_metric(m) for m in bitcoin_pagination.items]

    ethereum_pagination = Metric.query.filter_by(metric_type='crypto_ethereum') \
        .order_by(Metric.timestamp.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)
    ethereum_metrics = [reconstruct_metric(m) for m in ethereum_pagination.items]

    return render_template('history.html',
                           system_metrics=system_metrics,
                           bitcoin_metrics=bitcoin_metrics,
                           ethereum_metrics=ethereum_metrics,
                           system_pagination=system_pagination,
                           bitcoin_pagination=bitcoin_pagination,
                           ethereum_pagination=ethereum_pagination)

@app.route('/api/latest-metrics', methods=['GET'])
def latest_metrics():
    metric = Metric.query.filter_by(metric_type='system') \
        .order_by(Metric.timestamp.desc()).first()
    if metric:
        sys_values = {mv.attribute_name: mv.attribute_value for mv in metric.values}
        sys_values['timestamp'] = metric.timestamp.isoformat()
        return jsonify(sys_values)
    return jsonify({"error": "No system metrics found"}), 404

@app.route('/api/aggregator', methods=['POST'])
def aggregator():

    api_key = request.headers.get('x-api-key')
    valid_keys = current_app.config.get("API_KEYS", [])
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    if api_key not in valid_keys:
        return jsonify({"error": "Invalid API key"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        responses = {}
        device_id = data.get("device_id")
        if not device_id:
            return jsonify({"error": "No device_id provided"}), 400

        # process system metrics
        if 'system' in data:
            sys_data = data['system']
            metric = Metric(device_id=device_id, metric_type='system')
            db.session.add(metric)
            db.session.flush()

            for key, value in sys_data.items():
                mv = MetricValue(metric_id=metric.id, attribute_name=key, attribute_value=value)
                db.session.add(mv)
            responses['system'] = "Inserted"

        # process crypto metrics
        if 'crypto' in data:
            crypto_data = data['crypto']
            for coin, coin_data in crypto_data.items():
                if coin_data:
                    metric = Metric(device_id=device_id, metric_type=f'crypto_{coin}')
                    db.session.add(metric)
                    db.session.flush()
                    for key, value in coin_data.items():
                        mv = MetricValue(metric_id=metric.id, attribute_name=key, attribute_value=value)
                        db.session.add(mv)
                    responses[coin] = "Inserted"

        db.session.commit()
        return jsonify({"status": "success", "details": responses}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/send-command', methods=['POST'])
def send_command():
    data = request.get_json()
    action = data.get("action")
    if not action:
        return jsonify({"error": "No action specified"}), 400

    print(f"Storing Command in Database: {action}")
    new_command = CommandQueue(action=action)
    db.session.add(new_command)
    db.session.commit()
    return jsonify({"status": "Command stored", "action": action})

@app.route('/get-command', methods=['GET'])
def get_command():
    command = CommandQueue.query.order_by(CommandQueue.created_at.asc()).first()
    if command:
        action = command.action
        print(f"Sending command to Home PC: {action}")
        return jsonify({"action": action})
    return jsonify({"action": None})

@app.route('/get-command/delete', methods=['POST'])
def delete_command():
    data = request.get_json()
    action = data.get("action")
    if not action:
        return jsonify({"error": "No action specified"}), 400
    command = CommandQueue.query.filter_by(action=action).first()
    if command:
        db.session.delete(command)
        db.session.commit()
        print(f"Deleted command: {action}")
        return jsonify({"status": "Command deleted"})
    return jsonify({"error": "Command not found"}), 404

@app.route('/metrics/<device_id>', methods=['GET'])
def metrics_by_device(device_id):
    metrics = Metric.query.filter_by(device_id=device_id) \
        .order_by(Metric.timestamp.desc()).limit(20).all()
    metrics_list = [reconstruct_metric(m) for m in metrics]
    # convert timestamps to ISO format for JSON serialization
    for m in metrics_list:
        if m.get('timestamp'):
            m['timestamp'] = m['timestamp'].isoformat()
    return jsonify(metrics_list)

@app.route('/api/device', methods=['GET', 'POST'])
def device_endpoint():
    if request.method == 'GET':
        device_name = request.args.get('name')
        if not device_name:
            return jsonify({"error": "Device name is required"}), 400
        device = Device.query.filter_by(name=device_name).first()
        if device:
            return jsonify({"id": device.id, "name": device.name})
        else:
            return jsonify({"error": "Device not found"}), 404

    elif request.method == 'POST':
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "Device name is required"}), 400
        existing_device = Device.query.filter_by(name=data["name"]).first()
        if existing_device:
            return jsonify({"id": existing_device.id, "name": existing_device.name}), 200
        new_device = Device(
            id=str(uuid.uuid4()),
            name=data["name"],
            description=data.get("description")
        )
        db.session.add(new_device)
        db.session.commit()
        return jsonify({"id": new_device.id, "name": new_device.name}), 201