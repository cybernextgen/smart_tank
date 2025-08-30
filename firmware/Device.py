from heater import Heater
from parameter_manager import MODE_AUTO, MODE_OFF, MODE_REMOTE, ParameterManager
from sensors import (
    CalibratedSensor,
    DS18B20Sensor,
    FreeMemorySensor,
    HX711Sensor,
    IPAddressSensor,
    UptimeSensor,
)


class Device:

    free_memory_sensor: FreeMemorySensor
    uptime_sensor: UptimeSensor
    ip_address_sensor: IPAddressSensor

    bottom_temperature_sensor: DS18B20Sensor
    top_temperature_sensor: DS18B20Sensor
    load_cell_1_sensor: HX711Sensor
    load_cell_2_sensor: HX711Sensor
    load_cell_3_sensor: HX711Sensor
    load_cell_4_sensor: HX711Sensor

    heater: Heater

    parameters: ParameterManager

    sensors_data = {}
    calibrated_sensors_data = {}

    def disable(self):
        if not self.heater or not self.parameters:
            return

        self.heater.set_power(0)
        if self.parameters.mode != MODE_OFF:
            parameters.mode = MODE_OFF

    def read_sensors_data(self):
        self.sensors_data = {}

        for sensor in [
            self.free_memory_sensor,
            self.uptime_sensor,
            self.ip_address_sensor,
            self.bottom_temperature_sensor,
            self.load_cell_1_sensor,
        ]:
            self.sensors_data[sensor.name] = sensor.get_measurement().to_dict()
