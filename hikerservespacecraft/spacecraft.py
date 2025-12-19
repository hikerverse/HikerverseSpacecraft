import uuid
from typing import List

from hikerservespacecraft.active_component import ActiveComponent
from hikerservespacecraft.hull import Hull
from hikerservespacecraft.payloads.computer.spacecraft_computer import SpacecraftComputer
from hikerservespacecraft.payloads.propulsion.thruster import Thruster
from hikerservespacecraft.power_component import PowerComponent
from hikerservespacecraft.spacecraft_bus import SpacecraftBus, PowerBus
from hikerservespacecraft.tickable import Tickable


class Spacecraft(Tickable):
    """A spacecraft with various components, a spacecraft bus, and a power bus."""

    def __init__(self, name, ident: str = None, hull: Hull = None):
        self.name: str = name
        self.ident: str = ident if ident is not None else uuid.uuid4().hex
        self.hull: Hull = hull

        self.spacecraft_components: List[ActiveComponent] = []
        self.spacecraft_bus: SpacecraftBus = SpacecraftBus()
        self.power_bus: PowerBus = PowerBus()

        self.spacecraft_computer = SpacecraftComputer(spacecraft_bus=self.spacecraft_bus, power_bus=self.power_bus,
                                                      name="main_computer",
                                                      description="Main Spacecraft Computer",
                                                      mass=10,
                                                      volume=0.1)
        self.mass: float = 0  # in kg

    def get_propulsion_components(self) -> List[ActiveComponent]:
        propulsion_components = []
        for component in self.spacecraft_components:
            if isinstance(component, Thruster):
                propulsion_components.append(component)
        return propulsion_components

    def add_spacecraft_component(self, component: ActiveComponent) -> None:
        self.spacecraft_components.append(component)
        self.mass += component.mass

        if isinstance(component, PowerComponent):
            self.power_bus.add_component(component)
        else:
            self.spacecraft_bus.add_component(component)



    def tick(self, dt_s):

        for component in self.power_bus.components.values():
            component.tick(dt_s)

        for component in self.spacecraft_bus.components.values():
            component.tick(dt_s)



    def __repr__(self):
        return f"Spacecraft(name={self.name}, ident={self.ident}, hull={self.hull})"
