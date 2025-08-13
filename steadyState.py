from collections import deque

class SteadyState:
    def __init__(self, size=10, tolerance=1.0):
        self.size = size
        self.tolerance = tolerance
        self.buffer = deque(maxlen=size)

    def addValue(self, value: float):
        """Add a new float value and perform the tolerance check."""
        self.buffer.append(value)
        if len(self.buffer) == self.size:
            return self._check_tolerance()
        else:
            return False  # Not enough values to check

    def _check_tolerance(self) -> bool:
        """Check if all values are within ±tolerance of the most recent value."""
        latest = self.buffer[-1]
        return all(abs(latest - v) <= self.tolerance for v in self.buffer)

    def get_buffer(self):
        """Return the current buffer as a list."""
        return list(self.buffer)