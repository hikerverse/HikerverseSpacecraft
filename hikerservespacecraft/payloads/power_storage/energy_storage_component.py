

from hikerservespacecraft.command_response import CommandResponse
from hikerservespacecraft.commandable import Commandable, command
from hikerservespacecraft.power_component import PowerComponent, POWER_STORAGE
from hikerservespacecraft.reference.component_attributes import get_component_data
from hikerservespacecraft.tickable import Tickable


class EnergyStorageComponent(Commandable, PowerComponent, Tickable):
    """
    Energy storage component.
    Note: attribute names kept for compatibility with the rest of the codebase.
    """
    category = "power/storage"

    def __init__(self, name: str, description: str, mass: float, volume: float):
        super().__init__(name=name, description=description, mass=mass, volume=volume, power_type=POWER_STORAGE)
        # defaults
        self.current_energy_level_GJ: float = 0.0
        self.max_capacity_GJ: float = 0.0
        self.current_power_flow_A: float = 0.0
        self.max_charging_rate_A: float = 0.0
        self.max_discharging_rate_A: float = 0.0

        # load persisted/default component data without destroying methods
        data = get_component_data(component=self) or {}
        if isinstance(data, dict):
            self.__dict__.update(data)

    def get_power(self) -> float:
        """Return the currently requested/flowing power value (units as stored)."""
        return float(self.current_power_flow_A)

    @command
    def get_current_capacity(self) -> CommandResponse:
        return_data = {"current_level_GJ": float(self.current_energy_level_GJ)}
        return CommandResponse(
            success=True,
            return_data=return_data,
            device_type=self.__class__.__name__,
            message=f"{self.name} current charge level: {self.current_energy_level_GJ}",
        )

    @command
    def get_max_capacity(self) -> CommandResponse:
        return_data = {"max_capacity_GJ": float(self.max_capacity_GJ)}
        return CommandResponse(
            success=True,
            return_data=return_data,
            device_type=self.__class__.__name__,
            message=f"{self.name} current charge level: {self.max_capacity_GJ}",
        )

    @command
    def get_max_charging_rate(self) -> CommandResponse:
        return_data = {"max_charging_rate_A": float(self.max_charging_rate_A)}
        return CommandResponse(
            success=True,
            return_data=return_data,
            device_type=self.__class__.__name__,
            message=f"{self.name} max charging ratel: {self.max_charging_rate_A}",
        )

    @command
    def get_max_discharging_rate(self) -> CommandResponse:
        return_data = {"max_discharging_rate_A": float(self.max_discharging_rate_A)}
        return CommandResponse(
            success=True,
            return_data=return_data,
            device_type=self.__class__.__name__,
            message=f"{self.name} max discharging ratel: {self.max_discharging_rate_A}",
        )

    def tick(self, dt_s: float) -> None:
        """
        Advance state by dt_s seconds.
        The attribute names imply electrical current but the implementation treats
        `current_power_flow_A` as an energy-rate compatible with `current_capacity_GJ`.
        Keep units consistent across the system when integrating.
        """
        try:
            dt = float(dt_s)
        except (TypeError, ValueError):
            dt = 0.0

        # integrate capacity
        self.current_energy_level_GJ += self.current_power_flow_A * dt

        # clamp
        if self.current_energy_level_GJ > self.max_capacity_GJ:
            self.current_energy_level_GJ = float(self.max_capacity_GJ)
        elif self.current_energy_level_GJ < 0.0:
            self.current_energy_level_GJ = 0.0


    def __repr__(self) -> str:
        return (
            f"<PowerStorageComponent name={getattr(self, 'name', '')} "
            f"capacity={self.current_energy_level_GJ}/{self.max_capacity_GJ}>"
        )

