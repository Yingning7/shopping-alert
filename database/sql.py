SCHEMA_NAME = "shopping_alert"
TABLE_PLATFORMS_NAME = "platforms"
TABLE_ITEMS_NAME = "items"
TABLE_SPECS_NAME = "specs"
TABLE_STATUS_NAME = "status"

CREATE_SCHEMA = f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME};"

CREATE_TABLE_PLATFORMS = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_PLATFORMS_NAME} (
    platform_id SERIAL PRIMARY KEY,
    platform TEXT NOT NULL UNIQUE
);
"""

CREATE_TABLE_ITEMS = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_ITEMS_NAME} (
    platform_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    currency TEXT NOT NULL,
    url TEXT NOT NULL
);
"""

CREATE_TABLE_SPECS = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_SPECS_NAME} (
    specs_id SERIAL PRIMARY KEY,
    platform_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    color TEXT NOT NULL,
    size TEXT NOT NULL
);
"""

CREATE_TABLE_STATUS = f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{TABLE_STATUS_NAME} (
    status_id SERIAL PRIMARY KEY,
    specs_id INTEGER NOT NULL,
    original_price DOUBLE PRECISION,
    current_price DOUBLE PRECISION NOT NULL,
    inventory INTEGER,
    in_stock BOOLEAN NOT NULL,
    asof TIMESTAMP NOT NULL
);
"""

CREATE_INDEX_ITEMS = f"CREATE INDEX IF NOT EXISTS idx_{TABLE_ITEMS_NAME}_platform_item ON {SCHEMA_NAME}.{TABLE_ITEMS_NAME} (platform_id, item_id);"
CREATE_INDEX_SPECS = f"CREATE INDEX IF NOT EXISTS idx_{TABLE_SPECS_NAME}_platform_item ON {SCHEMA_NAME}.{TABLE_SPECS_NAME} (platform_id, item_id);"
CREATE_INDEX_STATUS = f"CREATE INDEX IF NOT EXISTS idx_{TABLE_STATUS_NAME}_specs ON {SCHEMA_NAME}.{TABLE_STATUS_NAME} (specs_id);"

INITIALIZE_DB = f"""
{CREATE_SCHEMA}
{CREATE_TABLE_PLATFORMS}
{CREATE_TABLE_ITEMS}
{CREATE_TABLE_SPECS}
{CREATE_TABLE_STATUS}
{CREATE_INDEX_ITEMS}
{CREATE_INDEX_SPECS}
{CREATE_INDEX_STATUS}
"""

QUERY_PLATFORMS = f"SELECT platform_id, platform FROM {SCHEMA_NAME}.{TABLE_PLATFORMS_NAME};"

INSERT_PLATFORMS = f"""
INSERT INTO {SCHEMA_NAME}.{TABLE_PLATFORMS_NAME} (platform) VALUES (%(platform)s);
"""

QUERY_ITEMS = f"SELECT platform_id, item_id, name, brand, currency, url FROM {SCHEMA_NAME}.{TABLE_ITEMS_NAME};"

INSERT_ITEMS = f"""
INSERT INTO {SCHEMA_NAME}.{TABLE_ITEMS_NAME} (platform_id, item_id, name, brand, currency, url) VALUES (%(platform_id)s, %(item_id)s, %(name)s, %(brand)s, %(currency)s, %(url)s);
"""

QUERY_SPECS = f"SELECT specs_id, platform_id, item_id, color, size FROM {SCHEMA_NAME}.{TABLE_SPECS_NAME};"

INSERT_SPECS = f"""
INSERT INTO {SCHEMA_NAME}.{TABLE_SPECS_NAME} (platform_id, item_id, color, size) VALUES (%(platform_id)s, %(item_id)s, %(color)s, %(size)s);
"""

INSERT_STATUS = f"""
INSERT INTO {SCHEMA_NAME}.{TABLE_STATUS_NAME} (specs_id, original_price, current_price, inventory, in_stock, asof) VALUES (%(specs_id)s, %(original_price)s, %(current_price)s, %(inventory)s, %(in_stock)s, %(asof)s);
"""
