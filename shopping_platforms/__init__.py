from enum import Enum

from .runway import RunwayPlatform
from .zozotown import ZozotownPlatform


class PlatformName(Enum):
    RUNWAY = RunwayPlatform._platform
    ZOZOTOWN = ZozotownPlatform._platform


PLATFORM_CLS_SELECTOR = {
    PlatformName.RUNWAY: RunwayPlatform,
    PlatformName.ZOZOTOWN: ZozotownPlatform
}
