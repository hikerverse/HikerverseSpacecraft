
from hikerservespacecraft.command_response import CommandResponse
from hikerservespacecraft.commandable import command
from hikerservespacecraft.component import Component
from hikerservespacecraft.tickable import Tickable


class ActiveComponent(Component, Tickable):

    def __init__(self, name: str, description: str, mass: float, volume: float):
        super().__init__(name, description, mass, volume)
        self.is_active: bool = False
        self.max_operating_temperature: float = 0
        self.current_temperature: float = 0

    def _set_active_state(self, is_active: bool) -> CommandResponse:
        self.is_active = is_active
        status_text = "activated" if is_active else "deactivated"
        return CommandResponse(success=True,
                               device_type=self.__class__.__name__,
                               message=f"{self.name} {status_text}.")

    @command
    def activate(self) -> CommandResponse:
        """Activate the component"""
        return self._set_active_state(True)

    @command
    def deactivate(self) -> CommandResponse:
        """Deactivate the component"""
        return self._set_active_state(False)
