from hikerservespacecraft.payloads.propulsion.thrust_profile import ThrustProfile
from hikerservespacecraft.payloads.propulsion.thruster import Thruster
from hikerservespacecraft.reference.component_attributes import get_component_data


class SimpleElectricThruster(Thruster):

    def __init__(self, name, description, mass, volume, thrust_profile: ThrustProfile = None):
        super().__init__(name, description, mass, volume, thrust_profile)

        data = get_component_data(component=self)
        if data:
            self.__dict__.update(data)
