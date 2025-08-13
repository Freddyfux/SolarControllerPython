class PIDController:
    def __init__(self, Kp, Ki, Kd, setpoint=0.0):
        self.Kp = Kp  # Proportional gain
        self.Ki = Ki  # Integral gain
        self.Kd = Kd  # Derivative gain
        self.setpoint = setpoint  # Desired target value

        self._prev_error = 0.0
        self._integral = 0.0

    def update(self, measurement, dt):
        """
        Calculate PID output based on the measurement and time difference.

        :param measurement: Current value
        :param dt: Time interval since last update
        :return: Control output
        """
        error = self.setpoint - measurement
        self._integral += error * dt
        derivative = (error - self._prev_error) / dt if dt > 0 else 0.0

        output = (
            self.Kp * error +
            self.Ki * self._integral +
            self.Kd * derivative
        )

        self._prev_error = error
        return output

    def reset(self):
        """Reset the integral and previous error."""
        self._integral = 0.0
        self._prev_error = 0.0
        
        
"""
Example
import time
import random

PITCH_MAX = 70
PITCH_MIN = 30
PITCH_DIFFERENCE_MAX = PITCH_MAX - PITCH_MIN

SPEED_MAX = 70
SPEED_MIN = 45
SPEED_DIFFERENCE_MAX = SPEED_MAX - SPEED_MIN

pid = PIDController(Kp=1.0, Ki=0.0, Kd=0.0, setpoint=PITCH_MAX)
measurement = PITCH_MIN

for _ in range(50):
    dt = 0.1  # Simulate 0.1s time step
    control = pid.update(measurement, dt)
    speed = abs(control/PITCH_DIFFERENCE_MAX) * SPEED_DIFFERENCE_MAX + SPEED_MIN
    measurement += control * dt# + random.uniform(-0.5, 0.5)  # Simulated system with noise

    print(f"Measurement: {measurement:.2f}, Control: {control:.2f}, Speed: {speed: .2f}")
    time.sleep(dt)
    
    
OUTCOME:
Measurement: 34.00, Control: 40.00, Speed:  70.00
Measurement: 37.60, Control: 36.00, Speed:  67.50
Measurement: 40.84, Control: 32.40, Speed:  65.25
Measurement: 43.76, Control: 29.16, Speed:  63.22
Measurement: 46.38, Control: 26.24, Speed:  61.40
Measurement: 48.74, Control: 23.62, Speed:  59.76
Measurement: 50.87, Control: 21.26, Speed:  58.29
Measurement: 52.78, Control: 19.13, Speed:  56.96
Measurement: 54.50, Control: 17.22, Speed:  55.76
Measurement: 56.05, Control: 15.50, Speed:  54.69
Measurement: 57.45, Control: 13.95, Speed:  53.72
Measurement: 58.70, Control: 12.55, Speed:  52.85
Measurement: 59.83, Control: 11.30, Speed:  52.06
Measurement: 60.85, Control: 10.17, Speed:  51.35
Measurement: 61.76, Control: 9.15, Speed:  50.72
Measurement: 62.59, Control: 8.24, Speed:  50.15
Measurement: 63.33, Control: 7.41, Speed:  49.63
Measurement: 64.00, Control: 6.67, Speed:  49.17
Measurement: 64.60, Control: 6.00, Speed:  48.75
Measurement: 65.14, Control: 5.40, Speed:  48.38
Measurement: 65.62, Control: 4.86, Speed:  48.04
Measurement: 66.06, Control: 4.38, Speed:  47.74
Measurement: 66.45, Control: 3.94, Speed:  47.46
Measurement: 66.81, Control: 3.55, Speed:  47.22
Measurement: 67.13, Control: 3.19, Speed:  46.99
Measurement: 67.42, Control: 2.87, Speed:  46.79
Measurement: 67.67, Control: 2.58, Speed:  46.62
Measurement: 67.91, Control: 2.33, Speed:  46.45
Measurement: 68.12, Control: 2.09, Speed:  46.31
Measurement: 68.30, Control: 1.88, Speed:  46.18
Measurement: 68.47, Control: 1.70, Speed:  46.06
Measurement: 68.63, Control: 1.53, Speed:  45.95
Measurement: 68.76, Control: 1.37, Speed:  45.86
Measurement: 68.89, Control: 1.24, Speed:  45.77
Measurement: 69.00, Control: 1.11, Speed:  45.70
Measurement: 69.10, Control: 1.00, Speed:  45.63
Measurement: 69.19, Control: 0.90, Speed:  45.56
Measurement: 69.27, Control: 0.81, Speed:  45.51
Measurement: 69.34, Control: 0.73, Speed:  45.46
Measurement: 69.41, Control: 0.66, Speed:  45.41
Measurement: 69.47, Control: 0.59, Speed:  45.37
Measurement: 69.52, Control: 0.53, Speed:  45.33
Measurement: 69.57, Control: 0.48, Speed:  45.30
Measurement: 69.61, Control: 0.43, Speed:  45.27
Measurement: 69.65, Control: 0.39, Speed:  45.24
Measurement: 69.69, Control: 0.35, Speed:  45.22
Measurement: 69.72, Control: 0.31, Speed:  45.20
Measurement: 69.75, Control: 0.28, Speed:  45.18
Measurement: 69.77, Control: 0.25, Speed:  45.16
Measurement: 69.79, Control: 0.23, Speed:  45.14
"""