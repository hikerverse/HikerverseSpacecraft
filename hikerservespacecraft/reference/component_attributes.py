from hikerservespacecraft.component import Component

component_data = {
    "sensor/optical": {
        "BasicStarTracker": {
            "detector_resolution": (512, 512),  # pixels
            "field_of_view": 20  # degrees
        }
    },
    "propulsion/thruster": {
        "SimpleElectricThruster": {
            "max_thrust": 500,  # Newtons
        }
    },
    "power/storage": {
        "CesiumSulphurBattery": {
            "max_capacity": 100,  # GW
            "max_charging_rate": 10,  # GW
            "max_discharging_rate": 10,  # GW
            "max_operating_temperature": 1000
        }
    },
    "power/generation": {
        "SubspaceHarvester": {
            "maximum_power_output": 0.01,  # GW
            "efficiency": 0.2
        }

    }
}


def get_component_data(component: Component):
    class_name = component.__class__.__name__

    component_category = component.category

    if component_category in component_data:
        data = component_data[component_category]

        if class_name in data:
            data = data[class_name]

            for key, value in data.items():
                if key in component.__dict__:
                    component.__dict__[key] = value

            return component.__dict__
