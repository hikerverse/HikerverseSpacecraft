from hikerservespacecraft.payloads.energy_generation.subspace_harvester import SubspaceHarvester
from hikerservespacecraft.payloads.power_storage.cesium_sulphur_battery import CesiumSulphurBattery
from hikerservespacecraft.payloads.propulsion.linear_thrust_profile import LinearThrustProfile
from hikerservespacecraft.payloads.propulsion.simple_electric_thruster import SimpleElectricThruster
from hikerservespacecraft.payloads.sensors.optical_sensor import OpticalSensor
from hikerservespacecraft.spacecraft import Spacecraft


def get_initial_spacecraft() -> Spacecraft:
    sc_const = SpacecraftConstructor(spacecraft_name="Cool SC")
    sc_const.spacecraft.add_spacecraft_component(
        component=CesiumSulphurBattery(name="battery", description="test", mass=100, volume=1))

    sc_const.spacecraft.add_spacecraft_component(
        component=SubspaceHarvester(name="subspace_harvester", description="test", mass=100, volume=1))

    sc_const.spacecraft.add_spacecraft_component(
        component=SimpleElectricThruster(name="thruster", description="test", mass=100, volume=1,
                                         thrust_profile=LinearThrustProfile(min_thrust=0, max_thrust=100, min_power=0,
                                                                            max_power=100)))

    sc_const.spacecraft.add_spacecraft_component(
        component=OpticalSensor(name="telescope", description="test", mass=100, volume=1))

    return sc_const.spacecraft


class SpacecraftConstructor:

    def __init__(self, spacecraft_name, spacecraft=None):
        if spacecraft is None:
            self.spacecraft = Spacecraft(name=spacecraft_name)
        else:
            self.spacecraft = spacecraft


