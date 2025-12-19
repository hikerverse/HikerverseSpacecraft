from abc import ABC

from hikerservespacecraft.active_component import ActiveComponent

POWER_PRODUCER = 1
POWER_CONSUMER = -1
POWER_STORAGE = 0

class PowerComponent(ActiveComponent, ABC):
    category = "power"

    def __init__(self, name, description, mass, volume, power_type):
        super().__init__(name, description, mass, volume)
        self.power_type = power_type
