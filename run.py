import importlib
import logging

import yaml

from db import init_schema, check_table_exists, create_table, insert_data

logging.basicConfig(level=logging.INFO)

PLATFORM_CONFIGS = {
    'runway': 'configs/runway.yaml'
}

if __name__ == '__main__':
    init_schema()
    for platform_name, config_path in PLATFORM_CONFIGS.items():
        logging.info(f'Working on {platform_name}.')
        platform = importlib.import_module(platform_name)
        with open(config_path, 'r') as file:
            kwargs_list = yaml.safe_load(file)
        for kwargs in kwargs_list:
            logging.info(f'Working on {platform_name}: {kwargs}.')
            try:
                df = platform.scrape(**kwargs)
            except Exception as error:
                logging.error(f'Failed to scrape {kwargs}. Error: {error}')
            else:
                if not check_table_exists(platform.TABLE_NAME):
                    create_table(platform.TABLE_NAME, platform.TABLE_DEF, platform.INDEX_DEF)
                insert_data(platform.TABLE_NAME, platform.TABLE_DEF, df)
