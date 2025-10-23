import math
import time

from constantsAndDefines import (
    UpDownPosition,
    EastWestPosition,
    Constants,
    ControllerID
)
from compensatePosition import CompensatePosition
from pidController import PIDController
from steadyState import SteadyState

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

class SolarController:
    def __init__(self, hass):
        self.hass = hass
        self.controllerName = None
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
        self.upDownPosition = None

        self.pidController = PIDController(Kp=1.0, Ki=0.0, Kd=0.0, setpoint=0)

        self.compensateUpDownPosition = None
        self.pitchSteadyState = SteadyState()
        self.rollSteadyState = SteadyState()

    def setSolarControllerEntityID(self, controllerName):
        if controllerName == ControllerID.ONE_AXIS_ID or controllerName == ControllerID.TWO_AXIS_ID:
            self.controllerName = controllerName
            self.controllerEntityIdBase = Constants.DEVICE_NAME_PREFIX + controllerName
            self.statusEntityId = "binary_sensor." + self.controllerEntityIdBase + "_status"
            self.pitchEntityId = "sensor." + self.controllerEntityIdBase + "_mpu6050_pitch"
            self.rollEntityId = "sensor." + self.controllerEntityIdBase + "_mpu6050_roll"
            self.switchUpEntityId   = "switch." + self.controllerEntityIdBase + "_up"
            self.switchDownEntityId = "switch." + self.controllerEntityIdBase + "_down"
            self.switchEastEntityId   = "switch." + self.controllerEntityIdBase + "_east"
            self.switchWestEntityId   = "switch." + self.controllerEntityIdBase + "_west"
            self.lightSpeedUpDownEntityId = "light." + self.controllerEntityIdBase + "_speed_up_down"
            self.lightSpeedEastWestEntityId = "light." + self.controllerEntityIdBase + "_speed_east_west"
            self.pitchMaximas = Constants.Pitch(controllerName)

            self.compensateUpDownPosition = CompensatePosition(self.pitchMaximas.MIN, self.pitchMaximas.MAX)

            self.hass.log(f"Got:")
            self.hass.log(f" - controllerName: {self.controllerName}")
            self.hass.log(f" - pitch:")
            self.hass.log(f"   - MAX     : {self.pitchMaximas.MAX}")
            self.hass.log(f"   - MIN     : {self.pitchMaximas.MIN}")
            self.hass.log(f"   - Current : {self.getPitch()}")
            self.hass.log(f" - roll:")
            self.hass.log(f"   - MAX     : {Constants.Roll.MAX}")
            self.hass.log(f"   - MIN     : {Constants.Roll.MIN}")
            self.hass.log(f"   - Current : {self.getRoll()}")
        else:
            self.hass.log(f"Solar controller {controllerName} is not valid")

    def is1AxisSolarControl(self):
        return self.controllerName == ControllerID.ONE_AXIS_ID

    def isSolarControllerConnected(self):
        if self.getStatus() == 'on':
            return True
        else:
            return False

    def getQuantity(self, entityId):
        if entityId is not None:
            entityId = self.hass.get_state(entityId)
            return entityId
        return None

    def getStatus(self):
        return self.getQuantity(self.statusEntityId)

    def getPitch(self):
        return self.getQuantity(self.pitchEntityId)

    def getRoll(self):
        return self.getQuantity(self.rollEntityId)

    def getSunElevation(self):
        return self.getQuantity("sensor.sun_elevation")

    def getSunAzimuth(self):
        return self.getQuantity("sensor.sun_azimuth")

    def isBeforeNoon(self):
        return float(self.getSunAzimuth()) < 180

    def isUpMovementAllowed(self):
        if UpDownPosition.Protect == self.upDownPosition:
            return True
        elif self.isPitchDifferenceFarTooHigh():
            return True
        else:
            if self.is1AxisSolarControl():
                return not self.isBeforeNoon()
            else:
                return self.isBeforeNoon()

    def isDownMovementAllowed(self):
        if UpDownPosition.Protect == self.upDownPosition:
            return True
        elif self.isPitchDifferenceFarTooHigh():
            return True
        else:
            if self.is1AxisSolarControl():
                return self.isBeforeNoon()
            else:
                return not self.isBeforeNoon()

    def isEastMovementAllowed(self, eastWestPosition):
        if EastWestPosition.Protect == eastWestPosition:
            return True
        elif self.isRollDifferenceFarTooHigh(eastWestPosition):
            return True
        else:
            return False

    def isWestMovementAllowed(self, eastWestPosition):
        return True

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
        if self.is1AxisSolarControl():
            return self.getPitchDifference() < 0
        else:
            return self.getPitchDifference() > 0

    def isPositionTooHigh(self):
        if self.is1AxisSolarControl():
            return self.getPitchDifference() > 0
        else:
            return self.getPitchDifference() < 0

    def isPositionTooEast(self, eastWestPosition):
        return self.getRollDifference(eastWestPosition) < 0

    def isPositionTooWest(self, eastWestPosition):
        return self.getRollDifference(eastWestPosition) > 0

    def isPositionMaxUp(self):
        if self.is1AxisSolarControl():
            return float(self.getPitch()) > self.pitchMaximas.MAX
        else:
            return float(self.getPitch()) < self.pitchMaximas.MIN

    def isPositionMaxDown(self):
        if self.is1AxisSolarControl():
            return float(self.getPitch()) < self.pitchMaximas.MIN
        else:
            return float(self.getPitch()) > self.pitchMaximas.MAX

    def isPositionMaxEast(self):
        return float(self.getRoll()) > Constants.Roll.MAX

    def isPositionMaxWest(self):
        return float(self.getRoll()) < Constants.Roll.MIN

    def getPitchDifference(self):
        if UpDownPosition.MinimizeDifference == self.upDownPosition:
            wantedPosition = float(self.getSunElevation())
        elif UpDownPosition.Protect == self.upDownPosition:
            if self.is1AxisSolarControl():
                wantedPosition = self.pitchMaximas.MIN
                wantedPosition = clamp(wantedPosition, self.pitchMaximas.MAX, self.pitchMaximas.MIN)
            else:
                wantedPosition = self.pitchMaximas.MAX
                wantedPosition = clamp(wantedPosition, self.pitchMaximas.MIN, self.pitchMaximas.MAX)

        pitch = 90 - float(self.getPitch())
        difference = wantedPosition - pitch
        #self.hass.log("Diff=wantedPosition-Pitch: {:.2f}={:.2f}-{:.2f}".format(difference, wantedPosition, pitch))

        return difference

    def getRollDifference(self, eastWestPosition):
        if EastWestPosition.MinimizeDifference == eastWestPosition:
            wantedPosition = - (float(self.getSunAzimuth()) - 180)
        elif EastWestPosition.Protect == eastWestPosition:
            wantedPosition = 0

        wantedPosition = clamp(wantedPosition, Constants.Roll.MIN, Constants.Roll.MAX)
        roll = float(self.getRoll())
        difference = wantedPosition - roll
        #self.hass.log("Diff=wantedPosition-Roll: {:.2f}={:.2f}-{:.2f}".format(difference, wantedPosition, roll))

        return difference

    def isPitchDifferenceTooHigh(self):
        return math.fabs(self.getPitchDifference()) > 1

    def isRollDifferenceTooHigh(self, eastWestPosition):
        return math.fabs(self.getRollDifference(eastWestPosition)) > 1

    def isPitchDifferenceFarTooHigh(self):
        return math.fabs(self.getPitchDifference()) > 6

    def isRollDifferenceFarTooHigh(self, eastWestPosition):
        return math.fabs(self.getRollDifference(eastWestPosition)) > 6

    def logDifference(self, controller_name, timeout, axis, *args):
        """
        Logs either pitch or roll difference depending on the axis.
    
        Parameters:
            controller_name (str): Name of the controller
            timeout (int): Timeout value (0 or non-zero)
            axis (str): Either 'pitch' or 'roll'
            *args: Extra arguments to pass to the difference function (e.g., eastWestPosition)
        """
        if axis == "pitch":
            diff = self.getPitchDifference(*args)
        elif axis == "roll":
            diff = self.getRollDifference(*args)
        else:
            raise ValueError(f"Unknown axis: {axis}")
    
        if timeout != 0:
            self.hass.log(f"{controller_name} {axis} is justified diff={diff:.2f}")
        else:
            self.hass.log(f"{controller_name} timeout diff={diff:.2f}")
    
    def moveUpDown(self, controllerName, upDownPosition):

        self.setSolarControllerEntityID(controllerName)
        self.upDownPosition = upDownPosition

        if self.isSolarControllerConnected():
            timeout = Constants.TIMEOUT

            while self.isPitchDifferenceTooHigh() and timeout > 0:
                currentPitchDifference = self.getPitchDifference()

                if (self.pitchSteadyState.addValue(currentPitchDifference)):
                    self.hass.log("U/D Position is steady")
                    break

                control = self.pidController.update(measurement=currentPitchDifference, dt=Constants.PIDController.UPDATE_PERIOD)
                speed = Constants.Speed.MAX
                if (abs(control) < Constants.PIDController.THRESHOLD):
                    speed = abs(control/Constants.PIDController.THRESHOLD) * Constants.Speed.DIFFERENCE_MAX_WITHIN_THRESHOLD * self.compensateUpDownPosition.compensate(self.getPitch()) + Constants.Speed.MIN

                if self.isPositionTooLow() and self.isUpMovementAllowed():
                    if (self.isPositionMaxUp()):
                        self.hass.log("Position is up at maximum")
                        break
                    self.switchOnUp()
                    self.hass.log("Move up")
                elif self.isPositionTooHigh() and not self.isPositionMaxDown() and self.isDownMovementAllowed():
                    if (self.isPositionMaxDown()):
                        self.hass.log("Position is down at maximum")
                        break
                    self.switchOnDown()
                    self.hass.log("Move down")
                    speed = speed * Constants.Speed.DOWN_FACTOR
                else:
                    self.hass.log("U/D Position settled")
                    break

                self.hass.log(f"Speed {speed}")
                self.setUpDownSpeed(speed)

                time.sleep(Constants.PIDController.UPDATE_PERIOD)
                timeout = timeout - 1

            self.setUpDownSpeed(0)

            self.logDifference(controllerName, timeout, "pitch")

        else:
            self.hass.log(f"Solar controller {controllerName} is {self.getStatus()}")

    def moveEastWest(self, controllerName, eastWestPosition):

        if controllerName == ControllerID.ONE_AXIS_ID:
            self.hass.log(f"Solar controller {controllerName} East/West movement isn't available")
            return

        self.setSolarControllerEntityID(controllerName)

        if self.isSolarControllerConnected():
            timeout = Constants.TIMEOUT

            while self.isRollDifferenceTooHigh(eastWestPosition) and timeout > 0:
                currentRollDifference = self.getRollDifference(eastWestPosition)

                if (self.rollSteadyState.addValue(currentRollDifference)):
                    self.hass.log("E/W Position is steady")
                    break

                control = self.pidController.update(measurement=currentRollDifference, dt=Constants.PIDController.UPDATE_PERIOD)
                speed = Constants.Speed.MAX
                if (abs(control) < Constants.PIDController.THRESHOLD):
                   speed = abs(control/Constants.PIDController.THRESHOLD) * Constants.Speed.DIFFERENCE_MAX_WITHIN_THRESHOLD + Constants.Speed.MIN

                if self.isPositionTooEast(eastWestPosition) and self.isWestMovementAllowed(eastWestPosition):
                    if self.isPositionMaxWest():
                        self.hass.log("Position is West at maximum")
                        break
                    self.switchOnWest()
                    self.hass.log("Move west")
                    speed = speed * Constants.Speed.WEST_FACTOR
                elif self.isPositionTooWest(eastWestPosition) and self.isEastMovementAllowed(eastWestPosition):
                    if self.isPositionMaxEast():
                        self.hass.log("Position is East at maximum")
                        break
                    self.switchOnEast()
                    self.hass.log("Move east")
                else:
                    self.hass.log("E/W Position settled")
                    break

                self.hass.log(f"Speed {speed}")
                self.setEastWestSpeed(speed)

                time.sleep(Constants.PIDController.UPDATE_PERIOD)
                timeout = timeout - 1

            self.setEastWestSpeed(0)

            self.logDifference(controllerName, timeout, "roll", eastWestPosition)

        else:
            self.hass.log(f"Solar controller {controllerName} is {self.getStatus()}")
