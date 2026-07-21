# setup.py
from ucapi_framework import BaseSetupFlow, RequestUserInputScreen
from .config import Tide16DeviceConfig

class Tide16SetupFlow(BaseSetupFlow[Tide16DeviceConfig]):
    def get_manual_entry_screen(self) -> RequestUserInputScreen:
        return RequestUserInputScreen(
            title="miniDSP Tide16 Setup",
            fields=[
                {"id": "host", "label": "IP Address", "type": "text", "required": True},
                {"id": "port", "label": "Port", "type": "number", "default": 80},
                {"id": "name", "label": "Device Name", "type": "text", "default": "Tide16"},
            ]
        )

    def create_config_from_input(self, user_input: dict) -> Tide16DeviceConfig:
        host = user_input["host"]
        return Tide16DeviceConfig(
            device_id=f"tide16_{host.replace('.', '_')}",
            name=user_input.get("name", "Tide16"),
            host=host,
            port=int(user_input.get("port", 80)),
        )