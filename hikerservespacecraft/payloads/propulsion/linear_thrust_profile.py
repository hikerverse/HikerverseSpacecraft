from hikerservespacecraft.payloads.propulsion.thrust_profile import ThrustProfile


class LinearThrustProfile(ThrustProfile):

    def __init__(self, min_power: float, max_power: float, min_thrust: float, max_thrust: float):
        super().__init__()
        self.min_power = min_power
        self.max_power = max_power
        self.min_thrust = min_thrust
        self.max_thrust = max_thrust

    def get_thrust_at(self, power: float) -> float:
        if power < self.min_power or power > self.max_power:
            raise ValueError(f"Power must be between {self.min_power} and {self.max_power}")
        # Linear interpolation
        thrust = self.min_thrust + (power - self.min_power) * (self.max_thrust - self.min_thrust) / (self.max_power - self.min_power)
        return thrust

    def get_power_at(self, thrust: float) -> float:
        if thrust < self.min_thrust or thrust > self.max_thrust:
            raise ValueError(f"Thrust must be between {self.min_thrust} and {self.max_thrust}")
        # Linear interpolation
        power = self.min_power + (thrust - self.min_thrust) * (self.max_power - self.min_power) / (self.max_thrust - self.min_thrust)
        return power
