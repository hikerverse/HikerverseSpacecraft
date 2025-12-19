from hikerservespacecraft.power_component import POWER_STORAGE
from energy_storage_component import EnergyStorageComponent

class SimpleBattery(EnergyStorageComponent):

    def __init__(self, name, description, mass, volume, power_type=POWER_STORAGE):
        super().__init__(name, description, mass, volume, power_type)
        self.capacity_kwh = 100.0  # Example capacity
        self.current_charge_kwh = 50.0  # Example current charge

    def __repr__(self):
        return (f"SimpleBattery(name={self.name}, capacity_kwh={self.capacity_kwh}, "
                f"current_charge_kwh={self.current_charge_kwh})")
