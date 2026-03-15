from database import sql

def test_sql_constants():
    assert sql.SCHEMA_NAME == "shopping_alert"
    assert "CREATE SCHEMA IF NOT EXISTS shopping_alert;" in sql.CREATE_SCHEMA
    assert "CREATE TABLE IF NOT EXISTS shopping_alert.platforms" in sql.CREATE_TABLE_PLATFORMS
    assert "CREATE TABLE IF NOT EXISTS shopping_alert.items" in sql.CREATE_TABLE_ITEMS
    assert "CREATE TABLE IF NOT EXISTS shopping_alert.specs" in sql.CREATE_TABLE_SPECS
    assert "CREATE TABLE IF NOT EXISTS shopping_alert.status" in sql.CREATE_TABLE_STATUS
