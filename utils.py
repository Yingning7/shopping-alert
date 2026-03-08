from __future__ import annotations

from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from pathlib import Path
import tomllib

from shopping_platforms import Platform


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Shopping Alert")
    parser.add_argument(
        "--platform", 
        type=str, 
        choices=[platform.value for platform in Platform] + ["all"],
        required=True
    )
    return parser.parse_args()


def load_item_configs(path: Path) -> dict[str, list[str]]:
    with open(path, mode="rb") as fp:
        return tomllib.load(fp)


@dataclass(frozen=True)
class Config:
    platform_items: dict[Platform, list[str]]

    @classmethod
    def from_args(cls, args: Namespace) -> Config:
        item_configs = load_item_configs(Path(__file__).parent / "platform_configs.toml")
        if args.platform == "all":
            platform_items = {
                platform: item_configs[platform.value]["run_args"]
                for platform in Platform
            }
        else:
            platform = Platform(args.platform)
            platform_items = {platform: item_configs[platform.value]["run_args"]}
        return cls(platform_items=platform_items)
