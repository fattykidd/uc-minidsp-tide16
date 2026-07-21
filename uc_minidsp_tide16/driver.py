# driver.py
from ucapi_framework import BaseIntegrationDriver, BaseDeviceManager
from .config import Tide16DeviceConfig
from .device import Tide16Device
from .setup import Tide16SetupFlow
from .entities import (
    Tide16MediaPlayer,
    Tide16PresetSelect,
    Tide16SceneSelect,
    Tide16DiracSwitch,
    Tide16BTButton,
    Tide16RebootButton,
    Tide16StreamFormatSensor,
    Tide16StreamChannelsSensor,
    Tide16SampleRateSensor,
    Tide16CoordinatorSensor,
)

class Tide16Driver(BaseIntegrationDriver[Tide16Device, Tide16DeviceConfig]):
    def __init__(self) -> None:
        config_manager = BaseDeviceManager("config.json", Tide16DeviceConfig)
        setup_flow = Tide16SetupFlow(config_manager)

        super().__init__(
            device_class=Tide16Device,
            config_manager=config_manager,
            setup_flow=setup_flow,
            entity_classes=[
                Tide16MediaPlayer,
                Tide16PresetSelect,
                Tide16SceneSelect,
                Tide16DiracSwitch,
                Tide16BTButton,
                Tide16RebootButton,
                Tide16StreamFormatSensor,
                Tide16StreamChannelsSensor,
                Tide16SampleRateSensor,
                Tide16CoordinatorSensor,
            ],
        )