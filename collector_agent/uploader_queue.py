import time
import threading
import requests
import platform
import os
from app_config import AGGREGATOR_API_URL, COMMAND_API_URL, DEVICE_API_URL, API_KEY, HEADERS, COLLECTION_INTERVAL, RETRY_INTERVAL

# this file collects metrics from the local system and external api and sends them to the aggregator api using the sdk

# import your local metrics agent class and crypto functions
from collect_local import gather_local_metrics
from collect_crypto import fetch_bitcoin_and_ethereum

# import the metricsapi class from your sdk package
from metrics_sdk.api import MetricsAPI

# set api endpoints from config into local variables for consistency
aggregator_url = AGGREGATOR_API_URL
command_api_url = COMMAND_API_URL
device_api_url = DEVICE_API_URL

# set api credentials and headers from config into local variables
api_key = API_KEY
headers = HEADERS

# initialize the sdk metricsapi instance using the consistent aggregator url and api key
metrics_api = MetricsAPI(aggregator_url=aggregator_url, api_key=api_key)

def gather_all_metrics():
    # gather both local system metrics and crypto metrics
    local_data = gather_local_metrics()
    crypto_data = fetch_bitcoin_and_ethereum()

    # get the device name from the platform node
    device_name = platform.node()
    # get or register the device and get its id
    device_id = get_or_register_device(device_name)

    # create the payload with device id system metrics crypto metrics and timestamp
    payload = {
        "device_id": device_id,
        "system": local_data,
        "crypto": crypto_data,
        "timestamp": time.time()
    }
    return payload

def get_or_register_device(device_name):
    # try to get the device from the device api
    try:
        response = requests.get(f"{device_api_url}?name={device_name}", headers=headers)
        print(f"get {device_api_url}?name={device_name} - status {response.status_code} body {response.text}")
        if response.ok:
            device_info = response.json()
            if device_info and 'id' in device_info:
                # if the response is ok and the device info contains an id then return the device id
                return device_info['id']
        else:
            # if the device is not found then print device not found trying to register
            print("device not found trying to register")
    except Exception as e:
        # if there is an error retrieving the device then print the error
        print("error retrieving device", e)

    # try to register the device
    try:
        payload = {"name": device_name, "description": "auto registered device"}
        response = requests.post(device_api_url, json=payload, headers=headers, verify=False)
        print(f"post {device_api_url} - status {response.status_code} body {response.text}")
        if response.ok:
            device_info = response.json()
            if device_info and 'id' in device_info:
                # if the response is ok and the device info contains an id then return the device id
                return device_info['id']
    except Exception as e:
        # if there is an error registering the device then print the error
        print("error registering device", e)

    # if registration failed wait thirty seconds and retry
    print("failed to register device retrying in 30 seconds")
    time.sleep(30)
    return get_or_register_device(device_name)

def collector():
    # continuously gather metrics and use the sdk to send them
    while True:
        payload = gather_all_metrics()
        print("collected payload", payload)
        # send the collected metrics using the sdk post metrics method
        metrics_api.post_metrics(payload['device_id'], payload.get('system'), payload.get('crypto'))
        time.sleep(COLLECTION_INTERVAL)

def command_listener():
    # continuously check the server for remote commands and execute them
    while True:
        try:
            response = requests.get(command_api_url, headers=headers)
            if response.status_code != 200:
                # if the server response is not 200 wait five seconds and continue
                print(f"server responded with status {response.status_code} {response.text}")
                time.sleep(5)
                continue

            data = response.json()

            if "action" in data and data["action"]:
                # if there is an action in the response then execute the command
                print(f"received command {data['action']}")
                execute_command(data["action"])0

                # delete the command after execution by sending a post request
                delete_response = requests.post(f"{command_api_url}/delete", json={"action": data["action"]}, headers=headers)
                if delete_response.ok:
                    print(f"successfully deleted command {data['action']}")
                else:
                    print("failed to delete command from database")

        except requests.exceptions.RequestException as e:
            # if there is an error checking for commands then print the error and wait ten seconds
            print(f"error checking for commands {e}")
            time.sleep(10)

def execute_command(action):
    # map the action to the system command and execute it
    commands = {
        "open_task_manager": "taskmgr" if platform.system() == "windows" else "gnome-system-monitor",
        "open_notepad": "notepad" if platform.system() == "windows" else "gedit",
        "open_spotify": "spotify",
        "open_vscode": "code"
    }

    if action in commands:
        os.system(commands[action])
        print(f"executed command {action}")
    else:
        print(f"unknown command {action}")

def main():
    # start all background processes

    # create the collector thread to gather and send metrics using the sdk
    collector_thread = threading.Thread(target=collector, daemon=True)
    # create the flusher thread to retry sending cached payloads using the sdk
    flusher_thread = threading.Thread(target=metrics_api.run_flusher, daemon=True)
    # create the command listener thread to check for remote commands
    command_thread = threading.Thread(target=command_listener, daemon=True)

    collector_thread.start()
    flusher_thread.start()
    command_thread.start()

    # keep the main thread alive by sleeping in a loop
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
