import paho.mqtt.client as mqtt

# --- Configuration ---
BROKER_ADDRESS = "broker.emqx.io"  # A public test broker
TOPIC = "polibatam/homeassistant/#"

# 1. The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect, the subscriptions will be renewed.
    client.subscribe(TOPIC)
    print(f"Subscribed to topic: {TOPIC}")

# 2. The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # msg.topic is the topic string (e.g., "polibatam/iot/temperature")
    # msg.payload is the raw message data (usually bytes)
    payload_str = msg.payload.decode()
    print(f"[{msg.topic}] Received message: {payload_str}")

# --- Main Setup ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1) # Use VERSION1 for paho-mqtt
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_ADDRESS, 1883, 60) # 1883 is the default MQTT port

# Blocking call that processes network traffic, dispatches callbacks, and
# handles reconnecting. Keeps the script running.
client.loop_forever()
