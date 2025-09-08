from enum import IntEnum

class Constants():
    TIMEOUT = 90
    DEVICE_NAME_PREFIX = "esp32_solar_control_"

    class Pitch():
        def __init__(self, controller):
            if controller == ControllerID.ONE_AXIS_ID:
                self.MAX = 78 # Down
                self.MIN = 22 # Up
                self.DIFFERENCE_MAX = self.MAX - self.MIN
            elif controller == ControllerID.TWO_AXIS_ID:
                self.MAX = 64 # Down
                self.MIN = 27 # Up
                self.DIFFERENCE_MAX = self.MAX - self.MIN
        MAX = None
        MIN = None
        DIFFERENCE_MAX = None

    class Roll():
        MAX = 34  # East
        MIN = -19 # West
        DIFFERENCE_MAX = MAX - MIN

    class Speed():
        DOWN_FACTOR = 0.85
        WEST_FACTOR = 1.1
        MAX = 70
        MIN = 45
        DIFFERENCE_MAX = MAX - MIN
        MAX_WITHIN_THRESHOLD = 55
        DIFFERENCE_MAX_WITHIN_THRESHOLD = MAX_WITHIN_THRESHOLD - MIN

    class PIDController():
        THRESHOLD = 15
        UPDATE_PERIOD = 1 # s

class ControllerID():
    ONE_AXIS_ID = "1_axis"
    TWO_AXIS_ID = "2_axis"

class EastWestPosition(IntEnum):
    MinimizeDifference = 0
    Protect            = 1

class UpDownPosition(IntEnum):
    MinimizeDifference = 0
    Protect            = 1