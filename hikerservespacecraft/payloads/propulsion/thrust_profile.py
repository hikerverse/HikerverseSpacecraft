from abc import ABC, abstractmethod


class ThrustProfile(ABC):

    def __init__(self, min_power: float = 0.0, max_power: float = 0.0, min_thrust: float = 0.0,
                 max_thrust: float = 0.0):
        self.min_power: float = min_power
        self.max_power: float = max_power
        self.min_thrust: float = min_thrust
        self.max_thrust: float = max_thrust

    @abstractmethod
    def get_thrust_at(self, power):
        pass

    @abstractmethod
    def get_power_at(self, thrust):
        pass
