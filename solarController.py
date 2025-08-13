import math
import time

from pidController import PIDController
from steadyState import SteadyState

DEVICE_NAME_PREFIX = "esp32_solar_control_"
ONE_AXIS_ID = "1_axis"
TWO_AXIS_ID = "2_axis"

TIMEOUT = 60 # s

PITCH_MAX = 64 # Down
PITCH_MIN = 27 # Up
PITCH_DIFFERENCE_MAX = PITCH_MAX - PITCH_MIN

ROLL_MAX = 34  # East
ROLL_MIN = -19 # West
ROLL_DIFFERENCE_MAX = ROLL_MAX - ROLL_MIN

SPEED_DOWN_FACTOR = 0.85
SPEED_MAX = 65
SPEED_MIN = 50
SPEED_DIFFERENCE_MAX = SPEED_MAX - SPEED_MIN

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

class SolarController:
    def __init__(self, hass):
        self.hass = hass
        self.controllerEntityIdBase = None
        self.statusEntityId = None
        self.pitchEntityId = None
        self.rollEntityId = None
        self.switchUpEntityId = None
        self.switchDownEntityId = None
        self.switchEastEntityId = None
        self.switchWestEntityId = None
        self.lightSpeedUpDownEntityId = None
        self.lightSpeedEastWestEntityId = None

        self.pidController = PIDController(Kp=1.0, Ki=0.0, Kd=0.0, setpoint=0)

        self.pitchSteadyState = SteadyState()
        self.rollSteadyState = SteadyState()

    def getSolarControllerEntityID(self, controllerName):
        if controllerName == ONE_AXIS_ID or controllerName == TWO_AXIS_ID:
            self.controllerEntityIdBase = DEVICE_NAME_PREFIX + controllerName
            self.statusEntityId = "binary_sensor." + self.controllerEntityIdBase + "_status"
            self.pitchEntityId = "sensor." + self.controllerEntityIdBase + "_mpu6050_pitch"
            self.rollEntityId = "sensor." + self.controllerEntityIdBase + "_mpu6050_roll"
            self.switchUpEntityId   = "switch." + self.controllerEntityIdBase + "_up"
            self.switchDownEntityId = "switch." + self.controllerEntityIdBase + "_down"
            self.switchEastEntityId   = "switch." + self.controllerEntityIdBase + "_east"
            self.switchWestEntityId   = "switch." + self.controllerEntityIdBase + "_west"
            self.lightSpeedUpDownEntityId = "light." + self.controllerEntityIdBase + "_speed_up_down"
            self.lightSpeedEastWestEntityId = "light." + self.controllerEntityIdBase + "_speed_east_west"
        else:
            self.hass.log(f"Solar controller {controllerName} is not valid")

    def isSolarControllerConnected(self, status):
        if status == 'on':
            return True
        else:
            return False

    def getQuantity(self, entityId):
        if entityId is not None:
            entityId = self.hass.get_state(entityId)
            return entityId
        return None

    def getStatus(self, status):
        return self.getQuantity(status)

    def getPitch(self, pitch):
        return self.getQuantity(pitch)

    def getRoll(self, roll):
        return self.getQuantity(roll)

    def getSunElevation(self):
        return self.getQuantity("sensor.sun_elevation")

    def getSunAzimuth(self):
        return self.getQuantity("sensor.sun_azimuth")

    def switchOnUp(self):
        if self.hass.get_state(self.switchUpEntityId) == "off":
            self.hass.log(f"Switch on {self.switchUpEntityId}")
            self.hass.call_service("switch/turn_on", entity_id=self.switchUpEntityId)

    def switchOnDown(self):
        if self.hass.get_state(self.switchDownEntityId) == "off":
            self.hass.log(f"Switch on {self.switchDownEntityId}")
            self.hass.call_service("switch/turn_on", entity_id=self.switchDownEntityId)

    def switchOffUp(self):
        if self.hass.get_state(self.switchUpEntityId) == "on":
            self.hass.log(f"Switch off {self.switchUpEntityId}")
            self.hass.call_service("switch/turn_off", entity_id=self.switchUpEntityId)

    def switchOffDown(self):
        if self.hass.get_state(self.switchDownEntityId) == "on":
            self.hass.log(f"Switch off {self.switchDownEntityId}")
            self.hass.call_service("switch/turn_off", entity_id=self.switchDownEntityId)

    def switchOnEast(self):
        if self.hass.get_state(self.switchEastEntityId) == "off":
            self.hass.log(f"Switch on {self.switchEastEntityId}")
            self.hass.call_service("switch/turn_on", entity_id=self.switchEastEntityId)

    def switchOnWest(self):
        if self.hass.get_state(self.switchWestEntityId) == "off":
            self.hass.log(f"Switch on {self.switchWestEntityId}")
            self.hass.call_service("switch/turn_on", entity_id=self.switchWestEntityId)

    def switchOffEast(self):
        if self.hass.get_state(self.switchEastEntityId) == "on":
            self.hass.log(f"Switch off {self.switchEastEntityId}")
            self.hass.call_service("switch/turn_off", entity_id=self.switchEastEntityId)

    def switchOffWest(self):
        if self.hass.get_state(self.switchWestEntityId) == "on":
            self.hass.log(f"Switch off {self.switchWestEntityId}")
            self.hass.call_service("switch/turn_off", entity_id=self.switchWestEntityId)

    def setUpDownSpeed(self, speed):
        speed = clamp(int(speed*1.0 / 100 * 256), 0, 256)
        self.hass.log(f"Set speed of {self.lightSpeedUpDownEntityId} with {speed}")
        self.hass.call_service("light/turn_on", entity_id=self.lightSpeedUpDownEntityId, brightness=speed)

    def setEastWestSpeed(self, speed):
        speed = clamp(int(speed*1.0 / 100 * 256), 0, 256)
        self.hass.log(f"Set speed of {self.lightSpeedEastWestEntityId} with {speed}")
        self.hass.call_service("light/turn_on", entity_id=self.lightSpeedEastWestEntityId, brightness=speed)

    def isPositionTooLow(self):
        return self.getPitchDifference() > 0

    def isPositionTooHigh(self):
        return self.getPitchDifference() < 0

    def isPositionTooEast(self):
        return self.getRollDifference() > 0

    def isPositionTooWest(self):
        return self.getRollDifference() < 0

    def isPositionMaxUp(self):
        return float(self.getPitch(self.pitchEntityId)) < PITCH_MIN

    def isPositionMaxDown(self):
        return float(self.getPitch(self.pitchEntityId)) > PITCH_MAX

    def isPositionMaxEast(self):
        return float(self.getRoll(self.rollEntityId)) > ROLL_MAX

    def isPositionMaxWest(self):
        return float(self.getRoll(self.rollEntityId)) < ROLL_MIN

    def getPitchDifference(self):
        sunElevation = float(self.getSunElevation())
        sunElevation = clamp(sunElevation, PITCH_MIN, PITCH_MAX)
        pitch = 90 - float(self.getPitch(self.pitchEntityId))
        difference = sunElevation - pitch
        self.hass.log("Diff=Elevation-Pitch: {:.2f}={:.2f}-{:.2f}".format(difference, sunElevation, pitch))

        return difference

    def getRollDifference(self):
        sunAzimuth = float(self.getSunAzimuth()) - 180
        self.hass.log("Azimuth {:.2f}".format(sunAzimuth))
        sunAzimuth = clamp(sunAzimuth, ROLL_MIN, ROLL_MAX)
        roll = float(self.getRoll(self.rollEntityId))
        difference = sunAzimuth - roll
        self.hass.log("Diff=Azimuth-Roll: {:.2f}={:.2f}-{:.2f}".format(difference, sunAzimuth, roll))

        return difference

    def isPitchDifferenceTooHigh(self):
        return math.fabs(self.getPitchDifference()) > 3.0

    def isRollDifferenceTooHigh(self):
        return math.fabs(self.getRollDifference()) > 3.0

    def moveUpDown(self, controllerName):

        self.getSolarControllerEntityID(controllerName)
        status = self.getStatus(self.statusEntityId)

        if self.isSolarControllerConnected(status):
            timeout = TIMEOUT
            updatePeriod = 1 # s

            while self.isPitchDifferenceTooHigh() and timeout > 0:
                currentPitchDifference = self.getPitchDifference()

                if (self.pitchSteadyState.addValue(currentPitchDifference)):
                    self.hass.log("U/D Position is steady")
                    break

                control = self.pidController.update(measurement=currentPitchDifference, dt=updatePeriod)
                speed = abs(control/PITCH_DIFFERENCE_MAX) * SPEED_DIFFERENCE_MAX + SPEED_MIN

                if self.isPositionTooLow():
                    if (self.isPositionMaxUp()):
                        self.hass.log("Position is up at maximum")
                        break
                    self.switchOnUp()
                elif self.isPositionTooHigh() and not self.isPositionMaxDown():
                    if (self.isPositionMaxDown()):
                        self.hass.log("Position is down at maximum")
                        break
                    self.switchOnDown()
                    speed = speed * SPEED_DOWN_FACTOR
                else:
                    self.hass.log("U/D Position settled")
                    break

                self.setUpDownSpeed(speed)

                time.sleep(updatePeriod)
                timeout = timeout - 1

            self.switchOffUp()
            self.switchOffDown()
            self.setUpDownSpeed(0)

            if timeout != 0:
                self.hass.log("{} pitch is justified diff={:.2f}".format(controllerName, self.getPitchDifference()))
            else:
                self.hass.log("{} timeout diff={:.2f}".format(controllerName, self.getPitchDifference()))
        else:
            self.hass.log(f"Solar controller {solar_controller_name} is {solar_controller_status_state}")


    def moveEastWest(self, controllerName):

        self.getSolarControllerEntityID(controllerName)
        status = self.getStatus(self.statusEntityId)

        if self.isSolarControllerConnected(status):
            timeout = TIMEOUT
            updatePeriod = 1 # s

            while self.isRollDifferenceTooHigh() and timeout > 0:
                currentRollDifference = self.getRollDifference()

                if (self.rollSteadyState.addValue(currentRollDifference)):
                    self.hass.log("E/W Position is steady")
                    break

                control = self.pidController.update(measurement=currentRollDifference, dt=updatePeriod)
                speed = abs(control/ROLL_DIFFERENCE_MAX) * SPEED_DIFFERENCE_MAX + SPEED_MIN

                if self.isPositionTooEast():
                    if self.isPositionMaxWest():
                        self.hass.log("Position is West at maximum")
                        break
                    self.switchOnWest()
                elif self.isPositionTooWest():
                    if self.isPositionMaxEast():
                        self.hass.log("Position is East at maximum")
                        break
                    self.switchOnEast()
                else:
                    self.hass.log("E/W Position settled")
                    break

                self.setEastWestSpeed(speed)

                time.sleep(updatePeriod)
                timeout = timeout - 1

            self.switchOffEast()
            self.switchOffWest()
            self.setEastWestSpeed(0)

            if timeout != 0:
                self.hass.log("{} roll is justified diff={:.2f}".format(controllerName, self.getRollDifference()))
            else:
                self.hass.log("{} timeout diff={:.2f}".format(controllerName, self.getRollDifference()))

        else:
            self.hass.log(f"Solar controller {solar_controller_name} is {solar_controller_status_state}")