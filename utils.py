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
        choices=[p.value for p in Platform] + ["all"],
        required=True
    )
    return parser.parse_args()


def load_item_configs(path: Path) -> dict[str, list[str]]:
    with open(path, mode="rb") as fp:
        return tomllib.load(fp)


@dataclass(frozen=True)
class Config:
    p_items: dict[Platform, list[str]]

    @classmethod
    def from_args(cls, args: Namespace) -> Config:
        item_configs = load_item_configs(Path(__file__).parent / "item_configs.toml")
        if args.platform == "all":
            p_items = {
                p: item_configs[p.value]["item_args"]
                for p in Platform
            }
        else:
            p = Platform(args.platform)
            p_items = {p: item_configs[p.value]["item_args"]}
        return cls(p_items=p_items)
