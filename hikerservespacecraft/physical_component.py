from abc import ABC


class PhysicalComponent(ABC):
    def __init__(self, name: str, weight: float, dimensions: list):
        self.weight = weight  # in kilograms
        self.dimensions = dimensions  # (length, width, height) in centimeters

    def volume(self) -> float:
        length = self.dimensions[0]
        width = self.dimensions[1]
        height = self.dimensions[2]
        return length * width * height  # in cubic centimeters

    def density(self) -> float:
        vol = self.volume()
        if vol == 0:
            return 0
        return self.weight / (vol / 1000000)  # in kg/m^3
