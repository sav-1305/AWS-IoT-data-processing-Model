import paho.mqtt.client as mqtt
import ssl
import time
import json
import random
from datetime import datetime

ENDPOINT = "a13589391xayuj-ats.iot.ap-south-1.amazonaws.com"
PORT = 8883
TOPIC = "iot/sensor"

print(f"====Connecting to endpoint: {repr(ENDPOINT)}====\n")

DEVICE_IDS = [f"sensor-{i}" for i in range(1, 6)]

# Certs path
CA = "certs/AmazonRootCA1.pem"
CERT = "certs/certificate.pem.crt"
KEY = "certs/private.pem.key"

def generate_sensor_data(device_id):
    return {
        "device_id": device_id,
        "timestamp_epoch": int(time.time()),
        "timestamp_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "temperature_C": round(random.uniform(20.0, 80.0), 2),
        "pressure_kPa": round(random.uniform(95.0, 105.0), 2),
        "humidity_percent": round(random.uniform(30.0, 70.0), 2)
    }

client = mqtt.Client()
client.tls_set(ca_certs=CA, certfile=CERT, keyfile=KEY, tls_version=ssl.PROTOCOL_TLSv1_2)


def on_connect(client, userdata, flags, rc):
    print(f"\n====Connected to AWS IoT with result code {rc}====\n")

client.on_connect = on_connect
client.connect(ENDPOINT, PORT)
client.loop_start()

try:
    while True:
        for device_id in DEVICE_IDS:
            payload = generate_sensor_data(device_id)
            client.publish(TOPIC, json.dumps(payload), qos=1)
            print(f"|__| Published from {device_id}: {payload}")
            time.sleep(1)  # simulate ~1 second gap between each device
        time.sleep(3)  # simulate delay between full rounds
except KeyboardInterrupt:
    print("\n====Stopped simulation.====\n")
    client.loop_stop()