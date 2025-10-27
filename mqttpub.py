import paho.mqtt.client as mqtt
import time
import json # Useful for sending structured data

# --- Configuration ---
BROKER_ADDRESS = "broker.emqx.io"
TOPIC = "polibatam/homeassistant/airconditioner"

# --- Main Setup ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

try:
    client.connect(BROKER_ADDRESS, 1883, 60)
    client.loop_start()  # Start the background thread for network traffic
    print(f"Publisher connected to {BROKER_ADDRESS}")

    temperature = 25.0
    
    # Loop to continuously publish data
    while True:
        # Create a structured message (JSON)
        data = "true"        
        # Convert JSON object to a string for publishing
        
        # Publish the message
        result = client.publish(TOPIC, data)
        
        # Check result status (result[0] == 0 means success)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Published successfully to topic '{TOPIC}': {data}")
        else:
            print(f"Failed to publish message. Error code: {result.rc}")

        temperature += 0.1 # Simulate temp change
        time.sleep(5)      # Wait 5 seconds before next publish

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    client.loop_stop()
    client.disconnect()
