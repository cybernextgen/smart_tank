import re
import time

import machine
import ubinascii
import ujson
from machine import Pin, Signal, unique_id
from umqtt.robust import MQTTClient

import sheduler
from parameter_manager import MODE_AUTO, MODE_OFF, MODE_REMOTE, ParameterManager
from sensors import (
    QUALITY_BAD,
    QUALITY_GOOD,
    DS18B20Sensor,
    FreeMemorySensor,
    IPAddressSensor,
    UptimeSensor,
)
from wifi_manager import WifiManager

configuration_mode_signal = Signal(Pin(23, Pin.IN, Pin.PULL_UP), invert=True)

heater_output_signal = Signal(Pin(13, Pin.OUT))
heater_output_signal.value(0)

mqtt_client_id = ubinascii.hexlify(unique_id())
parameters = None
mqtt_client = None

wm = WifiManager(
    ssid="smart_tank",
    password="smart_tank",
    debug=True,
    configuration_mode=configuration_mode_signal.value(),
)

uptime_sensor = UptimeSensor()
free_memory_sensor = FreeMemorySensor()
ip_address_sensor = IPAddressSensor(wm)
bottom_temperature_sensor = DS18B20Sensor("bottom_temperature", 32, True)

ping_sheduler = sheduler.Sheduler(30000)


def make_mqtt_topic(path):
    return mqtt_client_id + path.encode()


def make_mqtt_input_topic(path):
    return make_mqtt_topic(f"/to_device{path}")


def make_mqtt_output_topic(path):
    return make_mqtt_topic(f"/from_device{path}")


def mqtt_message_handler(btopic, bmsg):

    if m := re.search(make_mqtt_input_topic("/parameters/(.+)"), btopic):
        parameter_name = m.group(1)
        try:
            setattr(parameters, parameter_name.decode(), int(bmsg))
        except Exception as e:
            print(e)
    elif btopic == make_mqtt_input_topic("/ping"):
        ping_sheduler.reset()
        mqtt_client.publish(make_mqtt_output_topic("/pong"), "")


def handle_sensors():
    sensors_data = {}
    for sensor in [
        free_memory_sensor,
        uptime_sensor,
        ip_address_sensor,
        bottom_temperature_sensor,
    ]:
        sensors_data[sensor.name] = sensor.get_measurement().to_dict()

    mqtt_client.publish(make_mqtt_output_topic("/sensors"), ujson.dumps(sensors_data))


def handle_off_mode():
    return


def handle_auto_mode():
    if parameters.mode != MODE_AUTO:
        return


def handle_remote_mode():
    if parameters.mode != MODE_REMOTE:
        ping_sheduler.reset()
        return

    if ping_sheduler.is_timeout():
        disable_device()
        return


def handle_output():
    pass


def disable_device():
    heater_output_signal.value(0)
    if parameters.mode != MODE_OFF:
        parameters.mode = MODE_OFF


def reset_device_after_delay(delay_sec=60):
    time.sleep(delay_sec)
    machine.reset()


def main():
    global mqtt_client_id, parameters, mqtt_client

    wm.connect()
    settings = wm.read_settings()

    mqtt_client_id = settings["device_name"].encode() or mqtt_client_id
    mqtt_host = settings["mqtt_host"]

    mqtt_client = MQTTClient(
        mqtt_client_id,
        mqtt_host,
        settings["mqtt_port"],
        settings["mqtt_user"],
        settings["mqtt_password"],
    )
    mqtt_client.set_callback(mqtt_message_handler)

    try:
        mqtt_client.connect()
        print(f"Connected to MQTT broker at {mqtt_host}")
        mqtt_client.subscribe(make_mqtt_input_topic("/#"))

    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")
        disable_device()
        reset_device_after_delay()

    parameters = ParameterManager(mqtt_client, make_mqtt_output_topic("/parameters"))

    sensor_sheduler = sheduler.Sheduler(10000)

    while True:
        try:
            mqtt_client.check_msg()

            if sensor_sheduler.is_timeout():
                handle_sensors()

            handle_auto_mode()
            handle_remote_mode()
            handle_output()

        except Exception as e:
            print(f"Error during MQTT operation: {e}")
            time.sleep(2)
            try:
                mqtt_client.reconnect()
            except Exception as reconnect_e:
                print(f"Failed to reconnect: {reconnect_e}")
                disable_device()
                reset_device_after_delay()


if __name__ == "__main__":
    main()
