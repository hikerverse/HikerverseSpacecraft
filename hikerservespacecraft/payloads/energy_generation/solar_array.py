from hikerservespacecraft.payloads.energy_generation.energy_generation_component import EnergyGenerationComponent
from hikerservespacecraft.reference.component_attributes import get_component_data


class SolarArray(EnergyGenerationComponent):

    def __init__(self, name, description, mass, volume, area, efficiency, power_per_m2):
        super().__init__(name=name, description=description, mass=mass, volume=volume)
        self.current_power_output = 0


        self.maximum_power_output = 0  # Pmax @ STC / 1000 W/m2
        self.efficiency = efficiency

        self.power_per_m2 = power_per_m2
        self.area = area





class G1SiliconSolarArray(SolarArray):
    category = "power/generation"

    def __init__(self, name, description, mass, volume):
        super().__init__(name=name, description=description, mass=mass, volume=volume)

        self.area = 1
        self.efficiency = 0.2
        self.current_power_output = 0
        self.maximum_power_output = 1000
        self.mass = 100
        self.volume = 100
        self.__dict__ = get_component_data(component=self)


    def tick(self, dt_s: float) -> None:
        self.current_power_output = self.area * self.efficiency * self.maximum_power_output
        pass
