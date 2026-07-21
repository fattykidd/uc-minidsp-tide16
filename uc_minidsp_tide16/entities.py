from ucapi.media_player import (
    MediaPlayerEntity, MediaPlayerFeatures, States as MediaStates, Commands as MediaCommands
)
from ucapi.select import SelectEntity, SelectCommands
from ucapi.switch import SwitchEntity, SwitchCommands
from ucapi.button import ButtonEntity, ButtonCommands
from ucapi.sensor import SensorEntity, SensorDeviceClass
from .device import Tide16Device

# --- MEDIA PLAYER ---
class Tide16MediaPlayer(MediaPlayerEntity):
    def __init__(self, device: Tide16Device) -> None:
        super().__init__(
            entity_id=f"media_player.{device.config.device_id}",
            name=device.config.name,
            features=[
                MediaPlayerFeatures.VOLUME_SET,
                MediaPlayerFeatures.VOLUME_UP_DOWN,
                MediaPlayerFeatures.MUTE_TOGGLE,
                MediaPlayerFeatures.MUTE,
                MediaPlayerFeatures.UNMUTE,
                MediaPlayerFeatures.SELECT_SOURCE,
            ],
        )
        self.device = device
        self.subscribe_to_device(device)

    def sync_state(self) -> None:
        state = MediaStates.ON if self.device.is_connected else MediaStates.OFF
        db = max(-127.5, min(0.0, self.device.volume_db))
        volume_pct = int(((db + 60.0) / 60.0) * 100) if db > -60.0 else 0

        # Filter out hidden inputs for the UI dropdown
        visible_sources = [
            self.device.source_names.get(src, src)
            for src in self.device.source_names
            if not self.device.hidden_sources.get(src, False)
        ]

        self.update({
            "state": state,
            "volume": max(0, min(100, volume_pct)),
            "muted": self.device.muted,
            "source": self.device.source_names.get(self.device.current_source, self.device.current_source),
            "source_list": visible_sources or list(self.device.source_names.values()),
        })

    async def handle_command(self, command: str, params: dict | None = None) -> None:
        params = params or {}
        if command == MediaCommands.VOLUME:
            target_db = -60.0 + (params.get("volume", 0) / 100.0) * 60.0
            await self.device.set_volume_db(target_db)
        elif command == MediaCommands.VOLUME_UP:
            await self.device.set_volume_db(min(0.0, self.device.volume_db + 1.0))
        elif command == MediaCommands.VOLUME_DOWN:
            await self.device.set_volume_db(max(-127.5, self.device.volume_db - 1.0))
        elif command == MediaCommands.MUTE_TOGGLE:
            await self.device.set_mute(not self.device.muted)
        elif command == MediaCommands.SELECT_SOURCE:
            selected_name = params.get("source")
            # Reverse lookup name to key
            for k, v in self.device.source_names.items():
                if v == selected_name:
                    await self.device.set_source(k)
                    break

# --- PRESET SELECT ---
class Tide16PresetSelect(SelectEntity):
    def __init__(self, device: Tide16Device) -> None:
        super().__init__(
            entity_id=f"select.{device.config.device_id}_preset",
            name=f"{device.config.name} Preset",
            options=[],
        )
        self.device = device
        self.subscribe_to_device(device)

    def sync_state(self) -> None:
        options = [p.get("name", f"Preset {i}") for i, p in enumerate(self.device.presets)]
        current = options[self.device.current_preset_index] if options and self.device.current_preset_index < len(options) else ""
        self.update({"options": options, "current_option": current})

    async def handle_command(self, command: str, params: dict | None = None) -> None:
        if command == SelectCommands.SELECT_OPTION and params:
            option = params.get("option")
            for idx, p in enumerate(self.device.presets):
                if p.get("name") == option or f"Preset {idx}" == option:
                    await self.device.set_preset(idx)
                    break

# --- SCENE SELECT ---
class Tide16SceneSelect(SelectEntity):
    def __init__(self, device: Tide16Device) -> None:
        super().__init__(
            entity_id=f"select.{device.config.device_id}_scene",
            name=f"{device.config.name} Scene",
            options=[],
        )
        self.device = device
        self.subscribe_to_device(device)

    def sync_state(self) -> None:
        options = [s.get("name", "") for s in self.device.scenes if "name" in s]
        self.update({"options": options, "current_option": self.device.current_scene})

    async def handle_command(self, command: str, params: dict | None = None) -> None:
        if command == SelectCommands.SELECT_OPTION and params:
            await self.device.set_scene(params.get("option", ""))

# --- DIRAC LIVE SWITCH ---
class Tide16DiracSwitch(SwitchEntity):
    def __init__(self, device: Tide16Device) -> None:
        super().__init__(
            entity_id=f"switch.{device.config.device_id}_dirac",
            name=f"{device.config.name} Dirac Live",
        )
        self.device = device
        self.subscribe_to_device(device)

    def sync_state(self) -> None:
        self.update({"state": "ON" if self.device.dirac_state else "OFF"})

    async def handle_command(self, command: str, params: dict | None = None) -> None:
        if command == SwitchCommands.TOGGLE:
            await self.device.set_dirac_state(not self.device.dirac_state)
        elif command == SwitchCommands.ON:
            await self.device.set_dirac_state(True)
        elif command == SwitchCommands.OFF:
            await self.device.set_dirac_state(False)

# --- SYSTEM BUTTONS ---
class Tide16BTButton(ButtonEntity):
    def __init__(self, device: Tide16Device) -> None:
        super().__init__(
            entity_id=f"button.{device.config.device_id}_pair_bt",
            name=f"{device.config.name} Pair Bluetooth",
        )
        self.device = device

    async def handle_command(self, command: str, params: dict | None = None) -> None:
        if command == ButtonCommands.PRESS:
            await self.device.set_bt_pairing_mode()

class Tide16RebootButton(ButtonEntity):
    def __init__(self, device: Tide16Device) -> None:
        super().__init__(
            entity_id=f"button.{device.config.device_id}_reboot",
            name=f"{device.config.name} Reboot",
        )
        self.device = device

    async def handle_command(self, command: str, params: dict | None = None) -> None:
        if command == ButtonCommands.PRESS:
            await self.device.reboot()

# --- SENSORS ---
class Tide16StreamFormatSensor(SensorEntity):
    def __init__(self, device: Tide16Device) -> None:
        super().__init__(
            entity_id=f"sensor.{device.config.device_id}_stream_format",
            name=f"{device.config.name} Audio Format",
        )
        self.device = device
        self.subscribe_to_device(device)

    def sync_state(self) -> None:
        self.update({"value": self.device.stream_format})

class Tide16StreamChannelsSensor(SensorEntity):
    def __init__(self, device: Tide16Device) -> None:
        super().__init__(
            entity_id=f"sensor.{device.config.device_id}_stream_channels",
            name=f"{device.config.name} Input Channels",
        )
        self.device = device
        self.subscribe_to_device(device)

    def sync_state(self) -> None:
        self.update({"value": self.device.stream_channels})

class Tide16SampleRateSensor(SensorEntity):
    def __init__(self, device: Tide16Device) -> None:
        super().__init__(
            entity_id=f"sensor.{device.config.device_id}_sample_rate",
            name=f"{device.config.name} Sample Rate",
        )
        self.device = device
        self.subscribe_to_device(device)

    def sync_state(self) -> None:
        self.update({"value": self.device.sample_rate})

class Tide16CoordinatorSensor(SensorEntity):
    def __init__(self, device: Tide16Device) -> None:
        super().__init__(
            entity_id=f"sensor.{device.config.device_id}_system_status",
            name=f"{device.config.name} Status",
        )
        self.device = device
        self.subscribe_to_device(device)

    def sync_state(self) -> None:
        self.update({"value": self.device.coordinator_status})