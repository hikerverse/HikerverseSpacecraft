


class Material:

    def __init__(self, name, density):
        self.name = name
        self.density = density  # in kg/m^3


class MaterialFactory:
    def __init__(self):
        self.materials = {}

    def create_material(self, name: str, density: float) -> Material:
        if name not in self.materials:
            material = Material(name, density)
            self.materials[name] = material
        return self.materials[name]

    @staticmethod
    def get_material(self, name: str) -> Material:
        return self.materials.get(name)

    def list_materials(self):
        return list(self.materials.keys())
