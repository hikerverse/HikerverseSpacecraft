from hikerservespacecraft.active_component import ActiveComponent
from hikerservespacecraft.commandable import Commandable
from hikerservespacecraft.reference.component_attributes import get_component_data
from hikerservespacecraft.universe_aware import UniverseAware
from hikerverseuniverse.sensor_physics.optical_sensor_implementation import OpticalSensorImpl
from hikerverseuniverse.utils.math_utils import gaussian_psf


class OpticalSensor(ActiveComponent, Commandable, UniverseAware):
    __serialize_exclude__ = {'telescope'}
    """Optical imaging sensor."""
    category = "sensor/optical"

    def __init__(self, name: str, description: str, mass: float, volume: float):
        super().__init__(name, description, mass, volume)


    # def take_image(self):
    #     OpticalSensorImpl.render(
    #         psf=gaussian_psf(3, 1),
    #         star_field=star_field,
    #         band_center_m=550e-9,
    #         aperture_diameter=1,
    #         fov_deg=45,
    #         resolution=(512, 512),
    #         telescope_position=cam_pos,
    #         camera_direction=cam_dir,
    #         up_hint=up_hint, threshold=threshold,
    #         exposure=exposure, saturation_limit=saturation_limit,
    #         blooming_factor=blooming_factor, log_scale=False,
    #         gain=1)
    #     )





class BasicStarTracker(OpticalSensor):
    """Basic star tracker for spacecraft attitude determination."""
    category = "sensor/optical"

    def __init__(self, name: str = "Basic Star Tracker",
                 description: str = "A simple star tracker for attitude determination.",
                 mass: float = 2.0, volume: float = 0.01):
        super().__init__(name, description, mass, volume)

        self.detector_resolution = (512, 512)  # pixels
        self.field_of_view = 10.0  # degrees
        self.__dict__ = get_component_data(component=self)

        # Configure basic star sensor parameters
        self.aperture_diameter = 0.05  # meters
        self.focal_length = 0.2  # meters


if __name__ == '__main__':
    star_tracker = BasicStarTracker()
    print(f"Created star tracker: {star_tracker.name}, FOV: {star_tracker.field_of_view} degrees")
