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
        self._pid_d = 0
        self._output_max_power = 70
        self._output_pwm_interval_ms = 1000
        self._top_temperature_ah = 80
        self._bottom_temperature_ah = 90
        self._bottom_temperature_sp = 70
        self._weight_sp = 5000

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

        self._load_parameters_from_file()
        self._publish_parameters()

    def _load_calibration_points_from_dict(self, target_dict, key):
        if points_from_file := target_dict.get(key):
            return [CalibrationPoint(**p) for p in points_from_file]

    def _serialize_calibration_points_to_dict(self, points):
        return [p.to_dict() for p in points]

    def _load_from_json(self, json_string):
        state_dict = ujson.loads(json_string)
        self._mode = state_dict.get("mode", self._mode)
        self._output_max_power = state_dict.get(
            "output_max_power", self._output_max_power
        )
        self._output_pwm_interval_ms = state_dict.get(
            "output_pwm_interval_ms", self._output_pwm_interval_ms
        )
        self._bottom_temperature_ah = state_dict.get(
            "bottom_temperature_ah", self._bottom_temperature_ah
        )
        self._bottom_temperature_sp = state_dict.get(
            "bottom_temperature_sp", self._bottom_temperature_sp
        )
        self._top_temperature_ah = state_dict.get(
            "top_temperature_ah", self._top_temperature_ah
        )
        self._weight_sp = state_dict.get("weight_sp", self._weight_sp)
        self._pid_p = state_dict.get("pid_p", self._pid_p)
        self._pid_i = state_dict.get("pid_i", self._pid_i)
        self._pid_d = state_dict.get("pid_d", self._pid_d)

        if cp := self._load_calibration_points_from_dict(
            state_dict, "weight_calibration_points"
        ):
            self._weight_calibration_points = cp

        if cp := self._load_calibration_points_from_dict(
            state_dict, "bottom_temperature_calibration_points"
        ):
            self._bottom_temperature_calibration_points = cp

        if cp := self._load_calibration_points_from_dict(
            state_dict, "top_temperature_calibration_points"
        ):
            self._top_temperature_calibration_points = cp

    def _serialize_to_json(self):
        return ujson.dumps(
            {
                "mode": self._mode,
                "output_max_power": self._output_max_power,
                "output_pwm_interval_ms": self._output_pwm_interval_ms,
                "bottom_temperature_ah": self._bottom_temperature_ah,
                "bottom_temperature_sp": self._bottom_temperature_sp,
                "top_temperature_ah": self._top_temperature_ah,
                "weight_sp": self._weight_sp,
                "pid_p": self._pid_p,
                "pid_i": self._pid_i,
                "pid_d": self._pid_d,
                "weight_calibration_points": self._serialize_calibration_points_to_dict(
                    self._weight_calibration_points
                ),
                "bottom_temperature_calibration_points": self._serialize_calibration_points_to_dict(
                    self._bottom_temperature_calibration_points
                ),
                "top_temperature_calibration_points": self._serialize_calibration_points_to_dict(
                    self._top_temperature_calibration_points
                ),
            }
        )

    def _save_parameters_to_file(self):
        with open(STATE_JSON_FILE_NAME, "w") as f:
            f.write(self._serialize_to_json())

    def _load_parameters_from_file(self):
        try:
            with open(STATE_JSON_FILE_NAME) as f:
                self._load_from_json(f.read())
        except Exception as e:
            self._save_parameters_to_file()

    def _publish_parameters(self):
        try:
            self.mqtt_client.publish(
                self.topic, self._serialize_to_json(), retain=True
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
        self._save_parameters_to_file()
        self._publish_parameters()

    @property
    def weight_calibration_points(self):
        return self._weight_calibration_points

    @weight_calibration_points.setter
    def weight_calibration_points(self, new_value):
        self._weight_calibration_points = new_value
        self._save_parameters_to_file()
        self._publish_parameters()

    @property
    def bottom_temperature_calibration_points(self):
        return self._bottom_temperature_calibration_points

    @bottom_temperature_calibration_points.setter
    def bottom_temperature_calibration_points(self, new_value):
        self._bottom_temperature_calibration_points = new_value
        self._save_parameters_to_file()
        self._publish_parameters()

    @property
    def top_temperature_calibration_points(self):
        return self._top_temperature_calibration_points

    @top_temperature_calibration_points.setter
    def top_temperature_calibration_points(self, new_value):
        self._top_temperature_calibration_points = new_value
        self._save_parameters_to_file()
        self._publish_parameters()

    @property
    def output_max_power(self):
        return self._output_max_power

    @output_max_power.setter
    def output_max_power(self, new_value):
        if new_value < 10 or new_value > 100:
            raise ValueError("Output max power value should be within 10...100%")

        self._output_max_power = new_value
        self._save_parameters_to_file()
        self._publish_parameters()

    @property
    def output_pwm_interval_ms(self):
        return self._output_pwm_interval_ms

    @output_pwm_interval_ms.setter
    def output_pwm_interval_ms(self, new_value):
        if new_value < 100 or new_value > 2000:
            raise ValueError("Output pwm interval value should be within 100...2000 ms")

        self._output_pwm_interval_ms = new_value
        self._save_parameters_to_file()
        self._publish_parameters()

    @property
    def bottom_temperature_ah(self):
        return self._bottom_temperature_ah

    @bottom_temperature_ah.setter
    def bottom_temperature_ah(self, new_value):
        self._bottom_temperature_ah = new_value
        self._save_parameters_to_file()
        self._publish_parameters()

    @property
    def bottom_temperature_sp(self):
        return self._bottom_temperature_sp

    @bottom_temperature_sp.setter
    def bottom_temperature_sp(self, new_value):
        self._bottom_temperature_sp = new_value
        self._save_parameters_to_file()
        self._publish_parameters()

    @property
    def top_temperature_ah(self):
        return self._top_temperature_ah

    @top_temperature_ah.setter
    def top_temperature_ah(self, new_value):
        self._top_temperature_ah = new_value
        self._save_parameters_to_file()
        self._publish_parameters()

    @property
    def weight_sp(self):
        return self._weight_sp

    @weight_sp.setter
    def weight_sp(self, new_value):
        self._weight_sp = new_value
        self._save_parameters_to_file()
        self._publish_parameters()

    @property
    def pid_i(self):
        return self._pid_i

    @pid_i.setter
    def pid_i(self, new_value):
        self._pid_i = new_value
        self._save_parameters_to_file()
        self._publish_parameters()

    @property
    def pid_p(self):
        return self._pid_p

    @pid_p.setter
    def pid_p(self, new_value):
        self._pid_p = new_value
        self._save_parameters_to_file()
        self._publish_parameters()

    @property
    def pid_d(self):
        return self._pid_d

    @pid_d.setter
    def pid_d(self, new_value):
        self._pid_d = new_value
        self._save_parameters_to_file()
        self._publish_parameters()
