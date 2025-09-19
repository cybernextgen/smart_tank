import re
import time

import machine
import scheduler
import ubinascii
import ujson
from heater import Heater
from machine import Pin, Signal, freq, unique_id
from device import Device
from parameter_manager import MODE_AUTO, MODE_OFF, MODE_REMOTE, ParameterManager
from sensors import CalibrationPoint, CalibratedSensor

from umqtt.robust import MQTTClient
from wifi_manager import WifiManager

configuration_mode_signal = Signal(Pin(23, Pin.IN, Pin.PULL_UP), invert=True)

mqtt_client_id = ubinascii.hexlify(unique_id())
parameters = None
mqtt_client = None

wifi_manager = WifiManager(
    ssid="smart_tank",
    password="smart_tank",
    configuration_mode=configuration_mode_signal.value(),
)

device = None

ping_sheduler = scheduler.Scheduler(30000)
weight_sp_count = 0


def make_mqtt_topic(path):
    return mqtt_client_id + path.encode()


def make_mqtt_input_topic(path):
    return make_mqtt_topic(f"/to_device{path}")


def make_mqtt_output_topic(path):
    return make_mqtt_topic(f"/from_device{path}")


def send_status(status_code=200, message="ok"):
    mqtt_client.publish(
        make_mqtt_output_topic("/status"),
        ujson.dumps({"status": status_code, "message": message}),
    )


def mqtt_message_handler(btopic, bmsg):
    if __debug__:
        print(f"Recieved MQTT message '{bmsg.decode()}' from topic '{btopic.decode()}'")

    if m := re.search(make_mqtt_input_topic("/parameters/(.+)"), btopic):
        parameter_name = m.group(1)
        try:
            if parameter_name in [
                b"mode",
                b"bottom_temperature_ah",
                b"top_temperature_ah",
                b"weight_sp",
            ]:
                if parameter_name == b"mode":
                    parameter_value = int(bmsg)
                else:
                    parameter_value = float(bmsg)
                setattr(device.parameters, parameter_name.decode(), parameter_value)
                send_status()
            elif parameter_name == b"bottom_temperature_sp":
                new_setpoint = float(bmsg)
                device.parameters.bottom_temperature_sp = new_setpoint
                device.temperature_regulator.setpoint = new_setpoint
                send_status()
            elif parameter_name == b"pid_p":
                new_p = float(bmsg)
                device.parameters.pid_p = new_p
                device.temperature_regulator.Kp = new_p
                send_status()
            elif parameter_name == b"pid_i":
                new_i = float(bmsg)
                device.parameters.pid_i = new_i
                device.temperature_regulator.Ki = new_i
                send_status()
            elif parameter_name == b"pid_d":
                new_d = float(bmsg)
                device.parameters.pid_d = new_d
                device.temperature_regulator.Kd = new_d
                send_status()
            elif parameter_name == b"output_max_power":
                new_limit = int(bmsg)
                device.parameters.output_max_power = new_limit
                device.heater.power_limit_percent = new_limit
                send_status()
            elif parameter_name == b"output_pwm_interval_ms":
                new_interval = int(bmsg)
                device.parameters.output_pwm_interval_ms = new_interval
                device.heater.pwm_interval_ms = new_interval
                send_status()

            elif parameter_name in [
                b"weight_calibration_points",
                b"bottom_temperature_calibration_points",
                b"top_temperature_calibration_points",
            ]:
                cp = [CalibrationPoint(**p) for p in ujson.loads(bmsg)]

                if parameter_name == b"weight_calibration_points":
                    device.parameters.weight_calibration_points = cp
                    device.wight_sensor_calibrated = CalibratedSensor(
                        device.weight_sensor,
                        *device.parameters.weight_calibration_points,
                    )
                elif parameter_name == b"bottom_temperature_calibration_points":
                    device.parameters.bottom_temperature_calibration_points = cp
                    device.bottom_temperature_sensor_calibrated = CalibratedSensor(
                        device.bottom_temperature_sensor,
                        *device.parameters.bottom_temperature_calibration_points,
                    )
                elif parameter_name == b"top_temperature_calibration_points":
                    device.parameters.top_temperature_calibration_points = cp
                    device.top_temperature_sensor_calibrated = CalibratedSensor(
                        device.top_temperature_sensor,
                        *device.parameters.top_temperature_calibration_points,
                    )
                send_status()

        except Exception as e:
            send_status(400, "Bad parameter name or parameter value")
    elif btopic == make_mqtt_input_topic("/ping"):
        ping_sheduler.reset()
        mqtt_client.publish(make_mqtt_output_topic("/pong"), "")
    elif btopic == make_mqtt_input_topic("/heater_power"):
        try:
            if device.parameters.mode == MODE_REMOTE:
                new_power = int(bmsg)
                device.heater.set_power(new_power)
                send_status()
            else:
                send_status(400, "Wrong device mode")
        except Exception as e:
            send_status(400, "Wrong power value")


def read_sensors_data():
    device.read_sensors_data()


def publish_sensors_data():
    sensors_data = {k: v.to_dict() for k, v in device.sensors_data.items()}
    mqtt_client.publish(make_mqtt_output_topic("/sensors"), ujson.dumps(sensors_data))


def handle_ah():
    if device.parameters.mode == MODE_OFF:
        return

    top_temperature_measurement = device.sensors_data.get(
        device.top_temperature_sensor_calibrated.name
    )

    bottom_temperature_measurement = device.sensors_data.get(
        device.bottom_temperature_sensor_calibrated.name
    )

    if not bottom_temperature_measurement or bottom_temperature_measurement.is_bad:
        disable_device()
        send_status(500, "Device disabled! Bottom temperature sensor malfunction.")
        return

    if bottom_temperature_measurement.value >= parameters.bottom_temperature_ah:
        disable_device()
        send_status(500, "Device disabled! Bottom temperature above AH setpoint.")
        return

    if (
        top_temperature_measurement
        and top_temperature_measurement.is_good
        and top_temperature_measurement.value >= parameters.top_temperature_ah
    ):
        disable_device()
        send_status(500, "Device disabled! Top temperature above AH setpoint.")
        return


def handle_sp():
    if device.parameters.mode == MODE_OFF:
        return

    current_weight = device.sensors_data.get(device.wight_sensor_calibrated.name)

    if current_weight.is_bad:
        disable_device()
        send_status(500, "Device disabled! Weight sensor malfunction.")
        return

    global weight_sp_count
    if current_weight.value > device.parameters.weight_sp:
        weight_sp_count = 0
    else:
        weight_sp_count += 1

    if weight_sp_count >= 20:
        weight_sp_count = 0
        disable_device()
        send_status(200, "Done! Weight setpoint reached.")
        return


def handle_off_mode():
    if device.parameters.mode != MODE_OFF:
        return
    disable_device()


def handle_auto_mode():
    if device.parameters.mode != MODE_AUTO:
        if device.temperature_regulator.auto_mode:
            device.temperature_regulator.auto_mode = False
        return

    if not device.temperature_regulator.auto_mode:
        current_power = device.heater_output_power_sensor.get_measurement()
        if current_power.is_bad:
            disable_device()
            send_status(500, "Device disabled! Heater output power sensor malfunction.")
            return
        device.temperature_regulator.set_auto_mode(
            True, last_output=current_power.value
        )

    current_temperature = device.sensors_data.get(
        device.bottom_temperature_sensor_calibrated.name
    )
    if current_temperature.is_bad:
        disable_device()
        send_status(500, "Device disabled! Bottom temperature sensor malfunction.")
        return

    new_output = device.temperature_regulator(current_temperature.value)
    if new_output:
        device.heater.set_power(round(new_output))


def handle_remote_mode():
    if device.parameters.mode != MODE_REMOTE:
        ping_sheduler.reset()
        return

    if ping_sheduler.is_timeout():
        disable_device()
        send_status(500, "Device disabled! Remote server not responded.")
        return


def handle_output():
    device.heater.handle_output()


def disable_device():
    device.heater.set_power(0)
    if device.parameters.mode != MODE_OFF:
        device.parameters.mode = MODE_OFF


def reset_device_after_delay(delay_sec=60):
    time.sleep(delay_sec)
    machine.reset()


def main():
    global mqtt_client_id, parameters, mqtt_client, device

    freq(160000000)

    wifi_manager.connect()
    settings = wifi_manager.read_settings()

    mqtt_client_id = settings.device_name.encode() or mqtt_client_id
    mqtt_host = settings.mqtt_host

    mqtt_client = MQTTClient(
        mqtt_client_id,
        mqtt_host,
        settings.mqtt_port,
        settings.mqtt_user,
        settings.mqtt_password,
    )
    mqtt_client.set_callback(mqtt_message_handler)

    try:
        mqtt_client.connect(clean_session=False)
        if __debug__:
            print(f"Connected to MQTT broker at '{mqtt_host}'")
        mqtt_client.subscribe(make_mqtt_input_topic("/#"))

    except Exception as e:
        if __debug__:
            print(f"Error connecting to MQTT broker: {e}")
        disable_device()
        reset_device_after_delay()

    parameters = ParameterManager(mqtt_client, make_mqtt_output_topic("/parameters"))

    device = Device(parameters, wifi_manager)

    read_sensors_data_scheduler = scheduler.Scheduler(1000)
    publish_sensors_data_scheduler = scheduler.Scheduler(5000)

    first_loop = True
    while True:
        try:
            mqtt_client.check_msg()

            if read_sensors_data_scheduler.is_timeout() or first_loop:
                read_sensors_data()
                handle_sp()

            if publish_sensors_data_scheduler.is_timeout() or first_loop:
                publish_sensors_data()

            first_loop = False

            handle_ah()
            handle_auto_mode()
            handle_remote_mode()
            handle_off_mode()
            handle_output()

        except Exception as e:
            if __debug__:
                print(f"Error during main loop operations: {e}")
            time.sleep(2)
            try:
                mqtt_client.reconnect()
            except Exception as reconnect_e:
                if __debug__:
                    print(f"Failed to reconnect: {reconnect_e}")
                disable_device()
                reset_device_after_delay()


if __name__ == "__main__":
    main()
