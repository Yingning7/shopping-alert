from types import ModuleType
from pathlib import Path
import logging

import yaml

import runway
import zozotown

from db import init_schema, check_table_exists, create_table, insert_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

platforms = {
    'runway': runway,
    'zozotown': zozotown
}


def main(platform_name: str, platform: ModuleType, items: list[str]) -> None:
    logger.info(f'Processing the platform: {platform_name}.')
    for item in items:
        logger.info(f'Processing the item: {item}.')
        df = platform.scrape(item)
        insert_data(df)
    logger.info(f'Finished for {platform_name}.')


if __name__ == '__main__':
    init_schema()
    if not check_table_exists():
        create_table()
    with open(Path(__file__).parent / Path('config.yaml'), mode='r') as fp:
        config = yaml.safe_load(fp)
    dfs = []
    for platform_name, platform in platforms.items():
        main(platform_name, platform, config[platform_name])
