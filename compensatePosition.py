import math

class CompensatePosition:
    def __init__(self, in_min=30, in_max=70, out_min=1.0, out_max=1.5, aggressiveness=3):
        self.in_min = in_min
        self.in_max = in_max
        self.out_min = out_min
        self.out_max = out_max
        self.aggressiveness = aggressiveness

    def compensate(self, x):
        """
        Maps input x from [in_min, in_max] to [out_min, out_max] using a more aggressive-than-exponential curve.

        Parameters:
            x (float): Input value.
            in_min (float): Minimum input value.
            in_max (float): Maximum input value.
            out_min (float): Minimum output value.
            out_max (float): Maximum output value.
            aggressiveness (float): Curve aggressiveness (>1 is steeper than exponential).

        Returns:
            float: Mapped output value.
        """
        # Clamp x to the input range
        x_clamped = max(min(x, self.in_max), self.in_min)

        # Normalize x to [0, 1]
        t = (x_clamped - self.in_min) / (self.in_max - self.in_min)

        # Apply an aggressive curve (super-exponential-like)
        curved = math.pow(t, self.aggressiveness ** 1.5)

        # Map to output range
        y = self.out_min + (self.out_max - self.out_min) * curved
        return y