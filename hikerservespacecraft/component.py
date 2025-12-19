

class Component:
    category = ""

    def __init__(self, name: str, description: str, mass: float, volume: float):
        self.name = name
        self.description = description
        self.mass = mass
        self.volume = volume
