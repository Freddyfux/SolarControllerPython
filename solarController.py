def getQuantityState(quantity):
    if quantity is not None:
        quantity_obj = hass.states.get(quantity)
        if quantity_obj:
            return quantity_obj.state
    return None

def getStatusState(status):
    return getQuantityState(status)

def getPitchState(pitch):
    return getQuantityState(pitch)

def isSolarControllerConnected(status):
    if status == 'on':
        return True
    else:
        return False

def waitUntilPitchReached():
    pass

def waitUntilRollReached():
    pass

def switchOnUp():
    service_data = {"entity_id": "switch.esp32_solar_control_1_axis_up"}
    hass.services.call("switch", "turn_on", service_data, False)

def switchOnDown():
    service_data = {"entity_id": "switch.esp32_solar_control_1_axis_down"}
    hass.services.call("switch", "turn_on", service_data, False)

def switchOffUp():
    service_data = {"entity_id": "switch.esp32_solar_control_1_axis_up"}
    hass.services.call("switch", "turn_off", service_data, False)

def switchOffDown():
    service_data = {"entity_id": "switch.esp32_solar_control_1_axis_down"}
    hass.services.call("switch", "turn_off", service_data, False)

def setUpDownSpeed(speed):
    speed = int(speed*1.0 / 100 * 256)
    service_data = {"entity_id": "light.esp32_solar_control_1_axis_speed_up_down", "brightness": speed}
    hass.services.call("light", "turn_on", service_data, False)

class SolarController:
    def __init__(self, name, status, pitch):
        self.name = name
        self.status = status
        self.pitch = pitch

def getSolarControllerFromInput():
    name = data.get("solar_controller_name") # "1-axis" or "2-axis"

    if name == ONE_AXIS_ID or name == TWO_AXIS_ID:
        logger.debug(f"Solar controller name is {name}")
        status = "binary_sensor." + DEVICE_NAME_PREFIX + name + "_status"
        pitch = "sensor." + DEVICE_NAME_PREFIX + name + "_mpu6050_pitch"
        return SolarController(name, status, pitch)
    else:
        logger.error(f"Solar controller {name} is not valid")
        return None

TIMEOUT = 10 # s
DEVICE_NAME_PREFIX = "esp32_solar_control_"

ONE_AXIS_ID = "1-axis"
TWO_AXIS_ID = "2-axis"

PITCH_HYSTERESIS_UPPER = 3.0
PITCH_HYSTERESIS_LOWER = 0.5

sc = getSolarControllerFromInput()

solar_controller_status_state = getStatusState(sc.status)
solar_controller_pitch_state = None

if isSolarControllerConnected(solar_controller_status_state):
    solar_controller_pitch_state = getPitchState(sc.pitch)
    logger.warning(f"Solar controller {sc.pitch} is: {solar_controller_pitch_state}")
    
    pitch = float(solar_controller_pitch_state)
    
    timeout = TIMEOUT
    if pitch > 0.0:
        switchOnUp()
        setUpDownSpeed(50)
        while (pitch > 0.0 and timeout > 0):
            pitch = float(getPitchState(sc.pitch))
            time.sleep(1)
            timeout = timeout - 1
            logger.warning("Positive pitch now negative")
        switchOffUp()
        setUpDownSpeed(0)
    
    elif pitch < 0.0:
        switchOnDown()
        setUpDownSpeed(50)
        while (pitch < 0.0 and timeout > 0):
            pitch = float(getPitchState(sc.pitch))
            time.sleep(1)
            timeout = timeout - 1
            logger.warning("Negative pitch now positive")
        switchOffDown()
        setUpDownSpeed(0)
else:
    logger.warning(f"Solar controller {solar_controller_name} is {solar_controller_status_state}")


