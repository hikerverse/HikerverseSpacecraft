from hikerservespacecraft.payloads.power_storage.energy_storage_component import EnergyStorageComponent
from hikerservespacecraft.reference.component_attributes import get_component_data


class CesiumSulphurBattery(EnergyStorageComponent):
    category = "power/storage"

    def __init__(self, name, description, mass, volume):
        super().__init__(name=name, description=description, mass=mass, volume=volume)

        self.__dict__ = get_component_data(component=self)

        self.current_capacity = 100
        self.current_power_flow = -10
        self.current_temperature = 0
        self.mass = 100
