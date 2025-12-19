from typing import Dict

from hikerservespacecraft.active_component import ActiveComponent
from hikerservespacecraft.power_component import PowerComponent


class PowerBus:
    def __init__(self):
        self.components: Dict[str, PowerComponent] = {}

    def add_component(self, component: PowerComponent):
        if component.name not in self.components:
            self.components[component.name] = component

class SpacecraftBus:

    def __init__(self):
        self.components: Dict[str, ActiveComponent] = {}

    def add_component(self, active_component: ActiveComponent):
        if active_component.name not in self.components:
            self.components[active_component.name] = active_component
