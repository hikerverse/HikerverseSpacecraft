from typing import Optional, Dict

from hikerservespacecraft.command_response import CommandResponse
from hikerservespacecraft.commandable import Commandable, command
from hikerservespacecraft.power_component import PowerComponent, POWER_PRODUCER
from hikerservespacecraft.reference.component_attributes import get_component_data
from hikerservespacecraft.tickable import Tickable


class EnergyGenerationComponent(Commandable, PowerComponent, Tickable):
    category = "power/generation"

    def __init__(
        self,
        name: str,
        description: str,
        mass: float,
        volume: float,
        maximum_power_output: float = 0.0,
        efficiency: float = 1.0,
        ramp_rate: float = 1e6,
    ) -> None:
        super().__init__(name=name, description=description, mass=mass, volume=volume, power_type=POWER_PRODUCER)

        # core state
        self.current_power_output: float = 0.0
        self.maximum_power_output: float = float(maximum_power_output)
        self.efficiency: float = float(max(0.0, min(1.0, efficiency)))
        self.enabled: bool = True
        self.target_output: Optional[float] = None
        self.ramp_rate: float = float(max(0.0, ramp_rate))

        # merge external component data without clobbering internal state
        data = get_component_data(component=self)
        if isinstance(data, dict):
            for k, v in data.items():
                # do not overwrite internal runtime-only attributes unless explicitly set
                if k in ("name", "description", "mass", "volume"):
                    setattr(self, k, v)
                elif k not in (
                    "current_power_output",
                    "maximum_power_output",
                    "efficiency",
                    "enabled",
                    "target_output",
                    "ramp_rate",
                ):
                    setattr(self, k, v)

    @command
    def activate(self) -> CommandResponse:
        self.current_power_output = self.maximum_power_output
        return self._set_active_state(True)

    @command
    def deactivate(self) -> CommandResponse:
        self.current_power_output = 0
        return self._set_active_state(False)


    @command
    def get_current_power_output(self):
        """Get the current power output in watts."""
        return_data = {"current_power_output": self.current_power_output}
        return CommandResponse(success=True,
                               return_data=return_data,
                               device_type=self.__class__.__name__,
                               message=f"{self.name} current power output: {self.current_power_output}")



    def get_power_flow(self) -> Dict[str, float]:
        """
        Return a snapshot of power flow values.
        Positive values indicate generated power in watts.
        """
        return {
            "generated_watts": float(self.current_power_output),
            "maximum_watts": float(self.maximum_power_output),
            "efficiency": float(self.efficiency),
            "enabled": 1.0 if self.enabled else 0.0,
        }

    def tick(self, dt_s) -> Optional[float]:
        """
        Advance internal state by delta_seconds.
        Adjusts current_power_output toward target_output (or maximum) at up to ramp_rate.
        Returns energy generated over the interval in joules (W * s) or None if disabled.
        """
        if dt_s <= 0:
            return 0.0

        if not self.enabled:
            # ramp down to zero
            desired = 0.0
        else:
            desired = (
                float(self.target_output)
                if self.target_output is not None
                else float(self.maximum_power_output)
            )
            desired = min(desired, self.maximum_power_output)
            desired = max(0.0, desired)

        delta_allowed = self.ramp_rate * float(dt_s)
        diff = desired - self.current_power_output
        if abs(diff) <= delta_allowed:
            self.current_power_output = desired
        else:
            self.current_power_output += delta_allowed if diff > 0 else -delta_allowed

        # apply efficiency to actual delivered/generated power
        generated = self.current_power_output * float(self.efficiency)
        energy_joules = generated * float(dt_s)
        return energy_joules



    @command
    def set_target_output(self, target_power: float) -> CommandResponse:
        """Set the target power output in watts. Args: target_power (float): Target power output in watts."""
        try:
            target_power = float(target_power)
        except (TypeError, ValueError):
            return CommandResponse(success=False, return_data={}, device_type=self.__class__.__name__,
                                   message="Invalid numeric value")

        if target_power < 0:
            return CommandResponse(success=False, return_data={}, device_type=self.__class__.__name__,
                                   message="Target output must be non-negative")

        self.target_output = min(target_power, self.maximum_power_output)
        return CommandResponse(success=True, return_data={"target_output": self.target_output},
                               device_type=self.__class__.__name__, message=f"Target set to {self.target_output} W")


    @command
    def set_maximum_power_output(self, watts: float) -> CommandResponse:
        try:
            watts = float(watts)
        except (TypeError, ValueError):
            return CommandResponse(success=False, return_data={}, device_type=self.__class__.__name__,
                                   message="Invalid numeric value")

        if watts < 0:
            return CommandResponse(success=False, return_data={}, device_type=self.__class__.__name__,
                                   message="Maximum must be non-negative")

        self.maximum_power_output = watts
        # clamp target/current if above new maximum
        if self.target_output is not None and self.target_output > watts:
            self.target_output = watts
        if self.current_power_output > watts:
            self.current_power_output = watts

        return CommandResponse(success=True, return_data={"maximum_power_output": self.maximum_power_output},
                               device_type=self.__class__.__name__,
                               message=f"Maximum power output set to {self.maximum_power_output} W")

    def get_maximum_power_output(self) -> float:
        return float(self.maximum_power_output)
