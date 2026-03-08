from __future__ import annotations
from typing import Any

from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from pathlib import Path
import tomllib

from shopping_platforms import PlatformName


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Shopping Alert")
    parser.add_argument(
        "--platform", 
        type=str, 
        choices=[platform_name.value for platform_name in PlatformName] + ["all"],
        required=True
    )
    return parser.parse_args()


def load_platform_configs(path: Path) -> dict[str, dict[str, Any]]:
    with open(path, mode="rb") as fp:
        return tomllib.load(fp)


@dataclass(frozen=True)
class Config:
    platforms_configs: dict[PlatformName, dict[str, Any]]

    @classmethod
    def from_args(cls, args: Namespace) -> Config:
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
