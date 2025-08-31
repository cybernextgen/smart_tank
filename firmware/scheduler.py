import time


class Sheduler:

    def __init__(self, interval):
        self.__interval = interval
        self.__last_execution_ticks = time.ticks_ms()

    def is_timeout(self):
        current_ticks = time.ticks_ms()
        if (
            time.ticks_diff(current_ticks, self.__last_execution_ticks)
            >= self.__interval
        ):
            self.__last_execution_ticks = current_ticks
            return True
        return False

    def reset(self):
        self.__last_execution_ticks = time.ticks_ms()
