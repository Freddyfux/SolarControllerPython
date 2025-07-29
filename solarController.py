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

def isSolarControllerConnected(solar_controller_status):
    if solar_controller_status == 'on':
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

TIMEOUT = 10 # s

ONE_AXIS_ID = "1-axis"
TWO_AXIS_ID = "2-axis"

PITCH_HYSTERESIS_UPPER = 3.0
PITCH_HYSTERESIS_LOWER = 0.5

solar_controller_name = data.get("solar_controller_name") # "1-axis" or "2-axis"
solar_controller_status = None
solar_controller_pitch = None

if solar_controller_name == ONE_AXIS_ID:
    logger.debug(f"Solar controller name is {solar_controller_name}")
    solar_controller_status = "binary_sensor.esp32_solar_control_1_axis_status"
    solar_controller_pitch = "sensor.esp32_solar_control_1_axis_mpu6050_pitch"
elif solar_controller_name == TWO_AXIS_ID:
    logger.debug(f"Solar controller name is {solar_controller_name}")
    solar_controller_status = "binary_sensor.esp32_solar_control_2_axis_status"
    solar_controller_pitch = "sensor.esp32_solar_control_2_axis_mpu6050_pitch"
else:
    logger.error(f"Solar controller name is not valid")

solar_controller_status_state = getStatusState(solar_controller_status)
solar_controller_pitch_state = None

if isSolarControllerConnected(solar_controller_status_state):
    solar_controller_pitch_state = getPitchState(solar_controller_pitch)
    logger.warning(f"Solar controller {solar_controller_pitch} is: {solar_controller_pitch_state}")
    
    pitch = float(solar_controller_pitch_state)
    
    timeout = TIMEOUT
    if pitch > 0.0:
        switchOnUp()
        setUpDownSpeed(50)
        while (pitch > 0.0 and timeout > 0):
            pitch = float(getPitchState(solar_controller_pitch))
            time.sleep(1)
            timeout = timeout - 1
            logger.warning("Positive pitch now negative")
        switchOffUp()
        setUpDownSpeed(0)
    
    elif pitch < 0.0:
        switchOnDown()
        setUpDownSpeed(50)
        while (pitch < 0.0 and timeout > 0):
            pitch = float(getPitchState(solar_controller_pitch))
            time.sleep(1)
            timeout = timeout - 1
            logger.warning("Negative pitch now positive")
        switchOffDown()
        setUpDownSpeed(0)
else:
    logger.warning(f"Solar controller {solar_controller_name} is {solar_controller_status_state}")


