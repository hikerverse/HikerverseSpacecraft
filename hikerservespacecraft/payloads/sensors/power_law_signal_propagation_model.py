import math


class PowerLawSignalPropagationModel:

    def __init__(self, exponent):
        self.exponent = exponent

    def get_signal(self, log_inital_power, distance):
        if distance == 0:
            return log_inital_power
        initial_power = math.pow(10, log_inital_power)
        signal = initial_power * 1.0/(math.pow(distance, self.exponent))
        return signal
