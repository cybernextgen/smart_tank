from wifi_manager import WifiManager
from machine import Pin, Signal, unique_id
from umqtt.robust import MQTTClient
import ubinascii
import time
import gc
import state

ENCODING = "utf-8"

configuration_mode_signal = Signal(Pin(23, Pin.IN, Pin.PULL_UP), invert=True)
mqtt_client_id = ubinascii.hexlify(unique_id())
device_state = None

wm = WifiManager(
    ssid="smart_tank",
    password="smart_tank",
    debug=True,
    configuration_mode=configuration_mode_signal.value(),
)


def sub_cb(topic, msg):

    if topic == mqtt_client_id + b"/state/change/mode":
        new_mode = msg.decode()
        try:
            device_state.mode = int(new_mode)
        except ValueError as e:
            print(e)
    print(f"Received message on topic {topic.decode()}: {msg.decode()}")


def main():
    wm.connect()
    settings = wm.read_settings()

    global mqtt_client_id
    mqtt_client_id = settings["device_name"].encode(ENCODING) or mqtt_client_id
    mqtt_host = settings["mqtt_host"]

    client = MQTTClient(
        mqtt_client_id,
        mqtt_host,
        settings["mqtt_port"],
        settings["mqtt_user"],
        settings["mqtt_password"],
    )
    client.set_callback(sub_cb)

    try:
        client.connect()
        print(f"Connected to MQTT broker at {mqtt_host}")
        client.subscribe(mqtt_client_id + b"/state/change/+")

    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")
        return

    global device_state
    device_state = state.DeviceState(
        client, mqtt_client_id + b"/" + "state".encode(ENCODING)
    )

    while True:
        try:
            client.check_msg()

            client.publish(mqtt_client_id, b"Hello from umqtt.robust!")
            time.sleep(5)
        except Exception as e:
            print(f"Error during MQTT operation: {e}")
            time.sleep(2)
            try:
                client.reconnect()
            except Exception as reconnect_e:
                print(f"Failed to reconnect: {reconnect_e}")


if __name__ == "__main__":
    main()
