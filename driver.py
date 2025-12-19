from pprint import pprint

from hikerservespacecraft.payloads.propulsion.thruster import Thruster
from hikerservespacecraft.spacecraft_constructor import get_initial_spacecraft
from hikerservespacecraft.utils.class_utils import analyze_command_methods_in_class

command_list = [
    {"device_id": "main_computer", "command": "boot", "args": {}},
    {"device_id": "main_computer", "command": "list_commandable_devices", "args": {}},
    {"device_id": "battery", "command": "activate", "args": {}},
    {"device_id": "subspace_harvester", "command": "activate", "args": {}},
    {"device_id": "thruster", "command": "activate", "args": {}},
    {"device_id": "subspace_harvester", "command": "get_current_power_output", "args": {}}
]



cmd2 = {
    "device_id": "thruster",
    "command": "set_thrust",
    "args": {
        "thrust": 100.0
    }
}

cmd3 = {
    "device_id": "thruster",
    "command": "get_thrust",
    "args": {}
}

if __name__ == "__main__":

    d = analyze_command_methods_in_class(cls=Thruster, wrapper_name="command")

    sc = get_initial_spacecraft()


    commandable_devices = sc.spacecraft_computer.list_commandable_devices()
    pprint(commandable_devices.return_data)

    sh_cmds = sc.spacecraft_computer.list_commands(device_id="subspace_harvester")
    pprint(sh_cmds)

    for _cmd in command_list:
        dd = sc.spacecraft_computer.route_command(cmd=_cmd)
        print(dd)

    for i in range(5):
        sc.tick(dt_s=1.0)
        dd = sc.spacecraft_computer.route_command(cmd=command_list[-1])
        print(dd)
