import ujson

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

        self.__load_parameters_from_file()
        self.__publish_parameters()

    def __load_from_json(self, json_string):
        state_dict = ujson.loads(json_string)
        self._mode = state_dict.get("mode", self._mode)

    def __serialize_to_json(self):
        return ujson.dumps({"mode": self._mode})

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
