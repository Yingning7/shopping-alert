from __future__ import annotations
from typing import Any
import logging

from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from pathlib import Path
import tomllib

from shopping_platforms import PlatformName

logger = logging.getLogger(__file__)


def parse_args() -> Namespace:
    logger.info("Parsing arguments.")
    parser = ArgumentParser(description="Shopping Alert")
    parser.add_argument(
        "--platform", 
        type=str, 
        choices=[platform_name.value for platform_name in PlatformName] + ["all"],
        required=True
    )
    return parser.parse_args()


def load_platform_configs(path: Path) -> dict[str, dict[str, Any]]:
    logger.info("Loading platform configs.")
    with open(path, mode="rb") as fp:
        return tomllib.load(fp)


@dataclass(frozen=True)
class Config:
    platforms_configs: dict[PlatformName, dict[str, Any]]

    @classmethod
    def from_args(cls, args: Namespace) -> Config:
        logger.info("Constructing config from arguments.")
        raw_platforms_configs = load_platform_configs(Path(__file__).parent / "configs/platforms.toml")
        if args.platform == "all":
            platforms_configs = {
                platform_name: raw_platforms_configs[platform_name.value]
                for platform_name in PlatformName
            }
        else:
            platform_name = PlatformName(args.platform)
            platforms_configs = {platform_name: raw_platforms_configs[platform_name.value]}
        return cls(platforms_configs=platforms_configs)
