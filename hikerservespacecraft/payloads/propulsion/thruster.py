from hikerservespacecraft.command_response import CommandResponse
from hikerservespacecraft.commandable import Commandable, command
from hikerservespacecraft.power_component import PowerComponent, POWER_CONSUMER
from hikerservespacecraft.payloads.propulsion.thrust_profile import ThrustProfile


class Thruster(Commandable, PowerComponent):
    category = "propulsion/thruster"

    def __init__(self, name: str, description: str, mass: float, volume: float,
                 thrust_profile: ThrustProfile = None):
        super().__init__(name=name, description=description, mass=mass, volume=volume, power_type=POWER_CONSUMER)
        self.thrust_profile: ThrustProfile = thrust_profile
        self.current_thrust: float = 0.0
        self.current_power: float = 0.0
        self.thrust_vector = (0.0, 0.0, 1.0)  # Default thrust vector pointing forward


    @command
    def set_thrust(self, thrust: float) -> CommandResponse:
        """Set the thruster's thrust level. Args: thrust (float): Desired thrust level."""
        if thrust < 0 or thrust > self.thrust_profile.max_thrust:
            raise ValueError(f"Thrust must be between 0 and {self.thrust_profile.max_thrust}")
        self.current_thrust = thrust
        self.current_power = self.thrust_profile.get_power_at(thrust=self.current_thrust)
        return CommandResponse(success=True,
                               device_type=self.__class__.__name__,
                               message=f"{self.name} thrust set to: {thrust}")

    @command
    def get_thrust(self) -> CommandResponse:
        """Get the current thrust level of the thruster."""
        return_data = {"thrust": self.current_thrust}
        return CommandResponse(success=True,
                               return_data=return_data,
                               device_type=self.__class__.__name__,
                               message=f"{self.name} current thrust: {self.current_thrust}")
