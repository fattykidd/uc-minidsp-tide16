from dataclasses import dataclass

@dataclass
class Tide16DeviceConfig:
    device_id: str
    name: str
    host: str
    port: int = 80