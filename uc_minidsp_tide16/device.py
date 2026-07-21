import json
import logging
from typing import Any
from ucapi_framework import WebSocketDevice
from .config import Tide16DeviceConfig

_LOGGER = logging.getLogger(__name__)

class Tide16Device(WebSocketDevice[Tide16DeviceConfig]):
    def __init__(self, config: Tide16DeviceConfig) -> None:
        super().__init__(config)
        # Audio / Master
        self.volume_db: float = -30.0
        self.muted: bool = False
        self.current_source: str = ""
        self.source_names: dict[str, str] = {}
        self.hidden_sources: dict[str, bool] = {}
        
        # Presets & Scenes
        self.current_preset_index: int = 0
        self.presets: list[dict[str, Any]] = []
        self.scenes: list[dict[str, Any]] = []
        self.current_scene: str = ""

        # Dirac Live
        self.dirac_state: bool = False
        self.dirac_measuring_mode: bool = False

        # Stream / Audio Decoder Telemetry
        self.stream_format: str = "Unknown"
        self.stream_channels: str = "0"
        self.sample_rate: str = "0 Hz"

        # System & Connectivity
        self.ip_address: str = ""
        self.bt_status: str = "Disconnected"
        self.coordinator_status: str = "Unknown"

    def get_websocket_url(self) -> str:
        return f"ws://{self.config.host}:{self.config.port}/ws"

    async def on_connected(self) -> None:
        """Query state for all available settings and telemetry on connect."""
        _LOGGER.info("Connected to Tide16 WebSocket at %s", self.config.host)
        endpoints = [
            "get_volume_db",
            "get_mute",
            "get_source",
            "get_source_names",
            "get_hidden_sources",
            "get_current_preset_index",
            "get_all_presets",
            "get_all_scenes",
            "get_dirac_state",
            "get_dirac_measuring_mode",
            "get_stream_properties",
            "get_coordinator_status",
            "get_ip",
            "get_bluetooth_status",
        ]
        for ep in endpoints:
            await self.send_command({"endpoint": ep})

    async def handle_message(self, message: str) -> None:
        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            _LOGGER.error("Failed to parse JSON: %s", message)
            return

        req = payload.get("req") or payload.get("notification") or payload.get("endpoint")
        data = payload.get("data") if "data" in payload else payload.get("value")

        # Map API Responses & Push Notifications
        if req in ("get_volume_db", "volume_change_db") and data is not None:
            self.volume_db = float(data)
        elif req in ("get_mute", "mute_change") and data is not None:
            self.muted = bool(data)
        elif req in ("get_source", "source_change") and data is not None:
            self.current_source = str(data)
        elif req == "get_source_names" and isinstance(data, dict):
            self.source_names = data
        elif req == "get_hidden_sources" and isinstance(data, dict):
            self.hidden_sources = data
        elif req in ("get_current_preset_index", "preset_change") and data is not None:
            self.current_preset_index = int(data)
        elif req == "get_all_presets" and isinstance(data, list):
            self.presets = data
        elif req == "get_all_scenes" and isinstance(data, list):
            self.scenes = data
        elif req in ("get_dirac_state", "dirac_change") and data is not None:
            self.dirac_state = bool(data)
        elif req == "get_dirac_measuring_mode" and data is not None:
            self.dirac_measuring_mode = bool(data)
        elif req in ("get_stream_properties", "stream_change") and isinstance(data, dict):
            self.stream_format = str(data.get("format", "PCM"))
            self.stream_channels = str(data.get("channels", "Stereo"))
            self.sample_rate = f"{data.get('sample_rate', 0)} Hz"
        elif req == "get_coordinator_status" and data is not None:
            self.coordinator_status = str(data)
        elif req == "get_ip" and data is not None:
            self.ip_address = str(data)
        elif req == "get_bluetooth_status" and data is not None:
            self.bt_status = str(data)

        self.push_update()

    async def send_command(self, payload: dict[str, Any]) -> None:
        if self.is_connected and self.ws:
            await self.ws.send_json(payload)

    # Audio Controls
    async def set_volume_db(self, db: float) -> None:
        await self.send_command({"endpoint": "set_volume_db", "value": round(db, 1)})

    async def set_mute(self, mute: bool) -> None:
        await self.send_command({"endpoint": "set_mute", "value": mute})

    async def set_source(self, source: str) -> None:
        await self.send_command({"endpoint": "set_source", "value": source})

    # Presets, Scenes & DSP
    async def set_preset(self, index: int) -> None:
        await self.send_command({"endpoint": "set_preset", "value": index})

    async def set_scene(self, scene_name: str) -> None:
        await self.send_command({"endpoint": "set_scene", "value": scene_name})

    async def set_dirac_state(self, enabled: bool) -> None:
        await self.send_command({"endpoint": "set_dirac_state", "value": enabled})

    # System Actions
    async def set_bt_pairing_mode(self) -> None:
        await self.send_command({"endpoint": "set_bt_pairing_mode"})

    async def reboot(self) -> None:
        await self.send_command({"endpoint": "reboot"})

    async def shutdown(self) -> None:
        await self.send_command({"endpoint": "shutdown"})