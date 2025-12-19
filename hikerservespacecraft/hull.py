import math

from hikerservespacecraft.component import Component

def _calculate_hull_weight(material: dict, thickness, dimensions: list) -> float:
    _outer = 4/3 * math.pi * dimensions[0]/2 * dimensions[1]/2 * dimensions[2]/2
    _inner = (4/3 * math.pi *
              (dimensions[0]-2*thickness)/2 *
              (dimensions[1]-2*thickness)/2 *
              (dimensions[2]-2*thickness)/2)
    volume_cm3 = _outer - _inner
    weight = material['density'] * volume_cm3
    return weight

class Hull(Component):

    def __init__(self, material: dict, thickness, name: str, dimensions: list):
        weight = _calculate_hull_weight(material, thickness, dimensions)

        super().__init__(name=name, description="Spacecraft Hull", mass=weight, volume=0)
        self.material: dict = material
        self.thickness = thickness

    def get_specs(self):
        return f"Hull Material: {self.material}, Thickness: {self.thickness} mm"

    def __repr__(self):
        return f"Hull(name={self.name}, material={self.material}, thickness={self.thickness},  mass={self.mass})"
