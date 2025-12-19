from hikerservespacecraft.payloads.energy_generation.energy_generation_component import EnergyGenerationComponent


class SubspaceHarvester (EnergyGenerationComponent):
    def __init__(self, name, description, mass, volume):
        super().__init__(name, description, mass, volume)
