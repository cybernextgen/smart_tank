import machine, time

PERIOD_FOR_50HZ = 20


class Heater:

    def __init__(
        self, output_pin_number: int, power_limit_percent=100, pwm_interval_ms=1000
    ):
        self.power_limit_percent = power_limit_percent
        self.pwm_interval_ms = pwm_interval_ms
        self.__current_pulse_width = 0
        self.__current_power_percent = 0
        self.__prev_ticks = 0
        self.__output_state = 0
        self.__output_pin = machine.Pin(output_pin_number, machine.Pin.OUT)

    def set_power(self, new_power_percent: int):
        if new_power_percent < 0:
            new_power_percent = 0
        elif new_power_percent > 100:
            new_power_percent = 100

        self.__current_power_percent = new_power_percent
        new_pulse_width = (
            self.pwm_interval_ms * new_power_percent * self.power_limit_percent * 0.0001
        )

        if new_pulse_width < PERIOD_FOR_50HZ:
            new_pulse_width = 0
        elif new_pulse_width > (self.pwm_interval_ms - PERIOD_FOR_50HZ):
            new_pulse_width = self.pwm_interval_ms
        self.__current_pulse_width = new_pulse_width

    def get_power(self) -> int:
        return self.__current_power_percent

    def handle_output(self):
        current_ticks = time.ticks_ms()
        spent_ticks = time.ticks_diff(current_ticks, self.__prev_ticks)

        if spent_ticks >= self.pwm_interval_ms:
            self.__output_state = 1 if self.__current_pulse_width > 0 else 0
            self.__prev_ticks = current_ticks

        elif spent_ticks >= self.__current_pulse_width:
            self.__output_state = 0

        self.__output_pin.value(self.__output_state)
