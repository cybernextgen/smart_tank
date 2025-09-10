from heater import Heater
from parameter_manager import MODE_AUTO, MODE_OFF, MODE_REMOTE, ParameterManager
from wifi_manager import WifiManager
from sensors import (
    CalibratedSensor,
    DS18B20Sensor,
    FreeMemorySensor,
    HX711Sensor,
    IPAddressSensor,
    UptimeSensor,
    WeightSensor,
    HeaterOutputPowerSensor,
)
from PID import PID


class Device:

    free_memory_sensor: FreeMemorySensor
    uptime_sensor: UptimeSensor
    ip_address_sensor: IPAddressSensor

    bottom_temperature_sensor: DS18B20Sensor
    bottom_temperature_sensor_calibrated: CalibratedSensor

    top_temperature_sensor: DS18B20Sensor
    top_temperature_sensor_calibrated: CalibratedSensor

    weight_sensor: WeightSensor
    wight_sensor_calibrated: CalibratedSensor

    heater: Heater
    heater_output_power_sensor: HeaterOutputPowerSensor

    parameters: ParameterManager

    temperature_regulator: PID

    sensors_data = {}

    def __init__(self, parameters: ParameterManager, wifi_manager: WifiManager):
        self.parameters = parameters

        self.free_memory_sensor = FreeMemorySensor()
        self.uptime_sensor = UptimeSensor()
        self.ip_address_sensor = IPAddressSensor(wifi_manager)

        self.bottom_temperature_sensor = DS18B20Sensor(
            "bottom_temperature", pin_number=32, blocking_first_read=True
        )
        self.top_temperature_sensor = DS18B20Sensor(
            "top_temperature", pin_number=33, blocking_first_read=True
        )

        load_cell_1_sensor = HX711Sensor(
            "load_cell_1", dout_pin_number=36, sck_pin_number=25
        )
        load_cell_2_sensor = HX711Sensor(
            "load_cell_2", dout_pin_number=39, sck_pin_number=26
        )
        load_cell_3_sensor = HX711Sensor(
            "load_cell_3", dout_pin_number=34, sck_pin_number=27
        )
        load_cell_4_sensor = HX711Sensor(
            "load_cell_4", dout_pin_number=22, sck_pin_number=21
        )
        self.weight_sensor = WeightSensor(
            "weight",
            load_cell_1_sensor,
            load_cell_2_sensor,
            load_cell_3_sensor,
            load_cell_4_sensor,
        )

        self.heater = Heater(
            13, parameters.output_max_power, parameters.output_pwm_interval_ms
        )
        self.heater_output_power_sensor = HeaterOutputPowerSensor(
            "heater_output_power", self.heater
        )

        self.bottom_temperature_sensor_calibrated = CalibratedSensor(
            self.bottom_temperature_sensor,
            *parameters.bottom_temperature_calibration_points
        )
        self.top_temperature_sensor_calibrated = CalibratedSensor(
            self.top_temperature_sensor, *parameters.top_temperature_calibration_points
        )
        self.wight_sensor_calibrated = CalibratedSensor(
            self.weight_sensor, *parameters.weight_calibration_points
        )

        self.temperature_regulator = PID(
            parameters.pid_p,
            parameters.pid_i,
            parameters.pid_d,
            setpoint=parameters.bottom_temperature_sp,
            scale="s",
            sample_time=5,
            output_limits=[0, 100],
        )
        self.temperature_regulator.auto_mode = False

    def read_sensors_data(self):
        self.sensors_data = {}

        for sensor in [
            self.free_memory_sensor,
            self.uptime_sensor,
            self.ip_address_sensor,
            self.heater_output_power_sensor,
        ]:
            self.sensors_data[sensor.name] = sensor.get_measurement()

        for sensor, calibrated_sensor in [
            (self.bottom_temperature_sensor, self.bottom_temperature_sensor_calibrated),
            (self.top_temperature_sensor, self.top_temperature_sensor_calibrated),
            (self.weight_sensor, self.wight_sensor_calibrated),
        ]:
            m = sensor.get_measurement()
            self.sensors_data[sensor.name] = sensor.get_measurement()
            self.sensors_data[calibrated_sensor.name] = (
                calibrated_sensor.get_measurement(m)
            )

    def handle_output(self):
        self.heater.handle_output()
