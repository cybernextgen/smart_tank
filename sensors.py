import ujson
import gc
import time


QUALITY_GOOD = 0
QUALITY_BAD = 1


class Measurement:

    def __init__(self, value, quality):
        self.value = value
        self.quality = quality

    def to_dict(self):
        return {"value": self.value, "quality": self.quality}

    def to_json(self):
        return ujson.dumps(self.to_dict)


class Sensor:

    def __init__(self, name):
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
