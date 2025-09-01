import ujson
import gc
import time
import machine, onewire, ds18x20
import hx711
from heater import Heater


QUALITY_GOOD = 0
QUALITY_BAD = 1


class Measurement:

    def __init__(self, value, quality: int):
        self.value = value
        self.quality = quality

    def to_dict(self):
        return {"value": self.value, "quality": self.quality}

    def to_json(self):
        return ujson.dumps(self.to_dict)


class Sensor:

    def __init__(self, name: str):
        self.name = name

    def get_measurement(self):
        return Measurement(0, QUALITY_GOOD)


class FreeMemorySensor(Sensor):

    def __init__(self):
        super().__init__("free_memory")

    def get_measurement(self):
        return Measurement(gc.mem_free(), QUALITY_GOOD)


class UptimeSensor(Sensor):

    def __init__(self):
        self.__current_ticks = time.ticks_ms()
        self.__old_ticks = 0
        self.__uptime_ms = 0
        super().__init__("uptime")

    def get_measurement(self):
        self.__old_ticks = self.__current_ticks
        self.__current_ticks = time.ticks_ms()
        self.__uptime_ms = self.__uptime_ms + time.ticks_diff(
            self.__current_ticks, self.__old_ticks
        )
        return Measurement(self.__uptime_ms / 1000, QUALITY_GOOD)


class IPAddressSensor(Sensor):

    def __init__(self, wifi_manager):
        self.__wifi_manager = wifi_manager
        super().__init__("ip_address")

    def get_measurement(self):
        if not self.__wifi_manager.is_connected():
            return Measurement("0.0.0.0", QUALITY_BAD)

        ifconfig = self.__wifi_manager.get_address()
        return Measurement(ifconfig[0], QUALITY_GOOD)


class DS18B20Sensor(Sensor):

    def __init__(self, name, pin_number, blocking_first_read=False):
        self.__prev_measurement = None
        self.__prev_ticks = 0
        self.__ds_sensors = []

        try:
            self.__sensor_reader = ds18x20.DS18X20(
                onewire.OneWire(machine.Pin(pin_number))
            )
            self.__ds_sensors = self.__sensor_reader.scan()

            if blocking_first_read:
                self.get_measurement()
                time.sleep_ms(760)
        except onewire.OneWireError:
            if __debug__:
                print(f"DS18B20 not found on pin {pin_number}")

        super().__init__(name)

    def get_measurement(self):
        if not len(self.__ds_sensors):
            return Measurement(0, QUALITY_BAD)

        current_ticks = time.ticks_ms()
        if not self.__prev_measurement:
            self.__sensor_reader.convert_temp()
            self.__prev_ticks = current_ticks
            self.__prev_measurement = Measurement(0, QUALITY_BAD)

        elif time.ticks_diff(current_ticks, self.__prev_ticks) >= 750:
            accumulator = 0
            for sensor in self.__ds_sensors:
                accumulator += self.__sensor_reader.read_temp(sensor)

            self.__sensor_reader.convert_temp()
            self.__prev_ticks = current_ticks

            self.__prev_measurement = Measurement(
                accumulator / len(self.__ds_sensors), QUALITY_GOOD
            )

        return self.__prev_measurement


class HX711Sensor(Sensor):

    def __init__(
        self,
        name: str,
        dout_pin_number: int,
        sck_pin_number: int,
        readings_for_averaging=20,
    ):
        self.__readings_for_averaging = readings_for_averaging
        self.__prev_measurement = None
        self.__accumulator = 0
        self.__readings_count = 0

        try:
            self.__sensor_reader = hx711.HX711(dout_pin_number, sck_pin_number)
        except hx711.DeviceIsNotReady:
            self.__sensor_reader = None

        super().__init__(name)

    def get_measurement(self):
        if not self.__sensor_reader:
            return Measurement(0, QUALITY_BAD)

        try:
            current_value = self.__sensor_reader.read()
            self.__accumulator += current_value
            self.__readings_count += 1

            if self.__prev_measurement is None:
                self.__prev_measurement = Measurement(current_value, QUALITY_GOOD)

            if self.__readings_count == self.__readings_for_averaging:
                self.__prev_measurement = Measurement(
                    round(self.__accumulator / self.__readings_for_averaging),
                    QUALITY_GOOD,
                )
                self.__readings_count = 0
                self.__accumulator = 0

            return self.__prev_measurement

        except hx711.DeviceIsNotReady:
            return Measurement(0, QUALITY_BAD)


class WeightSensor(Sensor):

    def __init__(
        self,
        name: str,
        load_cell_1: HX711Sensor,
        load_cell_2: HX711Sensor,
        load_cell_3: HX711Sensor,
        load_cell_4: HX711Sensor,
    ):
        self.__load_cell_1 = load_cell_1
        self.__load_cell_2 = load_cell_2
        self.__load_cell_3 = load_cell_3
        self.__load_cell_4 = load_cell_4

        super().__init__(name)

    def get_measurement(self):

        accumulator = 0

        for cell in [
            self.__load_cell_1,
            self.__load_cell_2,
            self.__load_cell_3,
            self.__load_cell_4,
        ]:
            m = cell.get_measurement()

            if m.quality != QUALITY_GOOD:
                return Measurement(0, QUALITY_BAD)
            accumulator += m.value

        return Measurement(accumulator, QUALITY_GOOD)


class HeaterOutputPowerSensor(Sensor):

    def __init__(self, name: str, heater: Heater):
        self.__heater = heater
        super().__init__(name)

    def get_measurement(self):
        return Measurement(self.__heater.get_power(), QUALITY_GOOD)


class CalibrationPoint:

    def __init__(self, raw_value: float, calibrated_value: float):
        self.raw_value = raw_value
        self.calibrated_value = calibrated_value

    def to_dict(self):
        return {"raw_value": self.raw_value, "calibrated_value": self.calibrated_value}

    def to_json(self):
        return ujson.dumps(self.to_dict)


class CalibratedSensor(Sensor):

    def __init__(
        self,
        sensor,
        calibration_point_1: CalibrationPoint,
        calibration_point_2: CalibrationPoint,
    ):

        self.sensor = sensor
        self.__k = (
            calibration_point_2.calibrated_value - calibration_point_1.calibrated_value
        ) / (calibration_point_2.raw_value - calibration_point_1.raw_value)
        self.__b = (
            self.__k * calibration_point_1.raw_value
            - calibration_point_1.calibrated_value
        )
        super().__init__(f"{sensor.name}_calibrated")

    def get_measurement(self, raw_measurement: Measurement = None):
        if not raw_measurement:
            raw_measurement = self.sensor.get_measurement()

        calibrated_value = self.__k * raw_measurement.value - self.__b
        return Measurement(calibrated_value, raw_measurement.quality)
