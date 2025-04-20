import logging

import yaml

from runway.scraper import scrape
from runway.db import TABLE_NAME, create_table, insert_data
from db import SCHEMA_NAME, DB_CREDS, init_schema, check_table_exists

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    init_schema()
    if not check_table_exists(TABLE_NAME):
        create_table(SCHEMA_NAME, DB_CREDS)
    with open('./runway/runway.yaml', mode='r') as fp:
        item_ids = yaml.safe_load(fp)
    for item_id in item_ids:
        df = scrape(item_id)
        insert_data(SCHEMA_NAME, DB_CREDS, df)
