import datetime


class CommandResponse:
    def __init__(self, success: bool = False, message: str = "", device_type: str = None, return_data: dict = None):
        self.success: bool = success
        self.message: str = message
        self.device_type: str = device_type
        self.datestamp = datetime.datetime.now().isoformat()
        self.return_data: dict = return_data if return_data is not None else {}
        self.log: list[str] = []

    def add_log_entry(self, entry: str):
        timestamp = datetime.datetime.now().isoformat()
        self.log.append(f"[{timestamp}] {entry}")

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "message": self.message,
            "return": self.return_data
        }

    def __repr__(self):
        return (f"CommandResponse(success={self.success}, message='{self.message}', "
                f"device_type='{self.device_type}', datestamp='{self.datestamp}', return_data={self.return_data})")
