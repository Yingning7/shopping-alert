from enum import Enum

from .runway import RunwayPlatform
from .zozotown import ZozotownPlatform


class Platform(Enum):
    RUNWAY = RunwayPlatform._platform
    ZOZOTOWN = ZozotownPlatform._platform


PLATFORM_CLS = {
    Platform.RUNWAY: RunwayPlatform,
    Platform.ZOZOTOWN: ZozotownPlatform
}
