import ujson
from sensors import CalibrationPoint

MODE_OFF = 0
MODE_AUTO = 1
MODE_REMOTE = 2

STATE_JSON_FILE_NAME = "params.json"


class ParameterManager:

    def __init__(self, mqtt_client, topic):
        self.mqtt_client = mqtt_client
        self.topic = topic

        self._mode = MODE_OFF
        self._pid_p = 1
        self._pid_i = 10
        self._output_max_power = 70
        self._output_pwm_interval_ms = 1000

        self._weight_calibration_points = [
            CalibrationPoint(0, 0),
            CalibrationPoint(1, 1),
        ]

        self._bottom_temperature_calibration_points = [
            CalibrationPoint(0, 0),
            CalibrationPoint(1, 1),
        ]

        self._top_temperature_calibration_points = [
            CalibrationPoint(0, 0),
            CalibrationPoint(1, 1),
        ]

        self.__load_parameters_from_file()
        self.__publish_parameters()

    def __load_calibration_points_from_dict(self, target_dict, key):
        if points_from_file := target_dict.get(key):
            return [CalibrationPoint(**p) for p in points_from_file]

    def __serialize_calibration_points_to_dict(self, points):
        return [p.to_dict() for p in points]

    def __load_from_json(self, json_string):
        state_dict = ujson.loads(json_string)
        self._mode = state_dict.get("mode", self._mode)
        self._output_max_power = state_dict.get(
            "output_max_power", self._output_max_power
        )
        self._output_pwm_interval_ms = state_dict.get(
            "output_pwm_interval_ms", self._output_pwm_interval_ms
        )

        if cp := self.__load_calibration_points_from_dict(
            state_dict, "weight_calibration_points"
        ):
            self._weight_calibration_points = cp

        if cp := self.__load_calibration_points_from_dict(
            state_dict, "bottom_temperature_calibration_points"
        ):
            self._bottom_temperature_calibration_points = cp

        if cp := self.__load_calibration_points_from_dict(
            state_dict, "top_temperature_calibration_points"
        ):
            self._top_temperature_calibration_points = cp

    def __serialize_to_json(self):
        return ujson.dumps(
            {
                "mode": self._mode,
                "output_max_power": self._output_max_power,
                "output_pwm_interval_ms": self._output_pwm_interval_ms,
                "weight_calibration_points": self.__serialize_calibration_points_to_dict(
                    self._weight_calibration_points
                ),
                "bottom_temperature_calibration_points": self.__serialize_calibration_points_to_dict(
                    self._bottom_temperature_calibration_points
                ),
                "top_temperature_calibration_points": self.__serialize_calibration_points_to_dict(
                    self._top_temperature_calibration_points
                ),
            }
        )

    def __save_parameters_to_file(self):
        with open(STATE_JSON_FILE_NAME, "w") as f:
            f.write(self.__serialize_to_json())

    def __load_parameters_from_file(self):
        try:
            with open(STATE_JSON_FILE_NAME) as f:
                self.__load_from_json(f.read())
        except Exception as e:
            self.__save_parameters_to_file()

    def __publish_parameters(self):
        try:
            self.mqtt_client.publish(
                self.topic, self.__serialize_to_json(), retain=True
            )
        except Exception as e:
            pass

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, new_value):
        if new_value not in [MODE_OFF, MODE_AUTO, MODE_REMOTE]:
            raise ValueError("Wrong mode value")
        self._mode = new_value
        self.__save_parameters_to_file()
        self.__publish_parameters()

    @property
    def weight_calibration_points(self):
        return self._weight_calibration_points

    @weight_calibration_points.setter
    def weight_calibration_points(self, new_value):
        self._weight_calibration_points = new_value
        self.__save_parameters_to_file()
        self.__publish_parameters()

    @property
    def bottom_temperature_calibration_points(self):
        return self._bottom_temperature_calibration_points

    @bottom_temperature_calibration_points.setter
    def bottom_temperature_calibration_points(self, new_value):
        self._bottom_temperature_calibration_points = new_value
        self.__save_parameters_to_file()
        self.__publish_parameters()

    @property
    def top_temperature_calibration_points(self):
        return self._top_temperature_calibration_points

    @top_temperature_calibration_points.setter
    def top_temperature_calibration_points(self, new_value):
        self._top_temperature_calibration_points = new_value
        self.__save_parameters_to_file()
        self.__publish_parameters()

    @property
    def output_max_power(self):
        return self._output_max_power

    @output_max_power.setter
    def output_max_power(self, new_value):
        self._output_max_power = new_value
        self.__save_parameters_to_file()
        self.__publish_parameters()

    @property
    def output_pwm_interval_ms(self):
        return self._output_pwm_interval_ms

    @output_pwm_interval_ms.setter
    def output_pwm_interval_ms(self, new_value):
        self._output_pwm_interval_ms = new_value
        self.__save_parameters_to_file()
        self.__publish_parameters()
