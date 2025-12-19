from typing import Optional, List, Union

from hikerservespacecraft.active_component import ActiveComponent
from hikerservespacecraft.command_response import CommandResponse
from hikerservespacecraft.commandable import Commandable, command
from hikerservespacecraft.power_component import PowerComponent, POWER_PRODUCER, POWER_STORAGE
from hikerservespacecraft.utils.class_utils import find_methods_with_wrapper


class SpacecraftComputer(ActiveComponent, Commandable):
    category = "computer/spacecraft_computer"

    def __init__(self, name: str, description: str,
                 mass: float, volume: float, spacecraft_bus=None, power_bus=None):
        super().__init__(name, description, mass, volume)

        self.spacecraft_bus = spacecraft_bus
        self.power_bus = power_bus

        self.is_booted = False
        self.is_active = True


    @command
    def list_commandable_devices(self) -> CommandResponse:
        cmd_res = CommandResponse()

        bus_components = {**(self.spacecraft_bus.components or {}), **(self.power_bus.components or {}),
                          self.name: self}


        commandable_devices: dict[str, str] = {}
        for comp_name, comp in bus_components.items():
            if isinstance(comp, Commandable):
                try:
                    description = comp.get_class_docstring(comp.__name__)
                except Exception:
                    description = comp.__class__.__doc__ or ""
                commandable_devices[comp_name] = description



        cmd_res.add_log_entry(f"Listing commandable devices: {commandable_devices}")

        cmd_res.success = True
        cmd_res.return_data = {"commandable_devices": commandable_devices}
        cmd_res.device_type = self.__class__.__name__
        cmd_res.message = f"{self.name} listed commandable devices."
        return cmd_res

    @command
    def boot(self) -> CommandResponse:
        cmd_res = CommandResponse()

        if self.is_booted:
            cmd_res.add_log_entry(f"{self.name} is already booted.")
            cmd_res.success = True
            cmd_res.return_data = {}
            cmd_res.device_type = self.__class__.__name__
            cmd_res.message = f"{self.name} is already booted."
            return cmd_res

        has_energy_storage = any(
            comp for comp in self.power_bus.components.values() if
            isinstance(comp, PowerComponent) and comp.power_type == POWER_STORAGE)

        cmd_res.add_log_entry(f"Checking for energy storage components: "
                              f"{'found' if has_energy_storage else 'not found'}")

        has_energy_generation = any(
            comp for comp in self.power_bus.components.values() if
            isinstance(comp, PowerComponent) and comp.power_type == POWER_PRODUCER)

        cmd_res.add_log_entry(f"Checking for energy generation components: "
                              f"{'found' if has_energy_generation else 'not found'}")

        if not has_energy_storage:
            return CommandResponse(success=False,
                                   return_data={},
                                   device_type=self.__class__.__name__,
                                   message=f"{self.name} boot failed: No energy storage components found.")

        if not has_energy_generation:
            return CommandResponse(success=False,
                                   return_data={},
                                   device_type=self.__class__.__name__,
                                   message=f"{self.name} boot failed: No energy generation components found.")

        self.is_booted = True
        cmd_res.add_log_entry(f"Booting computer: {self.name}")
        cmd_res.success = True
        cmd_res.return_data = {}
        cmd_res.device_type = self.__class__.__name__
        cmd_res.message = f"{self.name} boot success."
        return cmd_res

    def list_commands(self, device_id: str) -> dict[str, Union[str, list[str]]]:
        ret = {}

        bus_components = {**(self.spacecraft_bus.components or {}), **(self.power_bus.components or {}),
                          self.name: self}
        if device_id in bus_components:
            component = bus_components[device_id]
            if isinstance(component, Commandable):
                cmd_methods = find_methods_with_wrapper(cls=component.__class__, wrapper_name="command")
                for meth in cmd_methods:
                    ret[meth] = component.get_docstring(meth)

        return ret

    def route_command(self, cmd: dict[str, Union[str, list[str]]]):

        device_id: Optional[str] = cmd.get("device_id", None)
        if device_id is None:
            return self.__get_error_response("-", None, "Device ID not specified")

        command_: Optional[str] = cmd.get("command", None)
        if command_ is None:
            return self.__get_error_response("-", None, "command not specified")

        args: list[str] = cmd.get("args", None)
        if args is None:
            return self.__get_error_response("-", None, "args not specified")

        if not self.is_booted and command_ != "boot":
            return self.__get_error_response("-", None, "Spacecraft Computer is not booted")

        bus_components = {**(self.spacecraft_bus.components or {}), **(self.power_bus.components or {}),
                          self.name: self}

        if device_id in bus_components:
            component = bus_components[device_id]
            if isinstance(component, Commandable):
                if isinstance(component, ActiveComponent):

                    cmd_methods = find_methods_with_wrapper(cls=component.__class__, wrapper_name="command")

                    if command_ not in cmd_methods:
                        return self.__get_error_response("-", None, f"Command {command_} not found for {device_id}")

                    if not component.is_active and command_ != "activate":
                        return {
                            "cmd": "capacity",
                            "args": None,
                            "return_type": None,
                            "value": 0,
                            "status": 1,
                            "message": f"{component.__class__.__name__} is offline"
                        }

                cmd_return = component.execute(cmd=command_, args=args)
                if cmd_return is None:
                    return self.__get_error_response("-", None, f"{device_id} not found")
                else:
                    return cmd_return
            else:
                return self.__get_error_response("-", None, f"{component.name} is not commandable")
        else:
            return self.__get_error_response("-", None, f"{device_id} not found")

    @staticmethod
    def __get_error_response(cmd: str, args: Optional[List[str]], message: str) -> dict:
        return {
            "cmd": cmd,
            "args": args,
            "return": None,
            "status": -1,
            "message": message
        }
