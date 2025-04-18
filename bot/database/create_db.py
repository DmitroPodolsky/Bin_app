from loguru import logger
from bot.database.sql_operations import execute


async def create_bins_table():
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS bins (
        id TEXT PRIMARY KEY,
        country TEXT,
        bank TEXT,
        brand TEXT,
        type TEXT,
        level TEXT
    );
    """
    await execute(create_table_sql)


async def create_users_table():
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id BIGINT PRIMARY KEY,
        username TEXT,
        count_collected_bins INTEGER DEFAULT 1,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        is_admin BOOLEAN DEFAULT FALSE
    );
    """
    await execute(create_table_sql)


async def create_groups_table():
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS groups (
        id BIGINT PRIMARY KEY,
        owner_id BIGINT NOT NULL,
        owner_username TEXT,
        count_collected_bins INTEGER DEFAULT 1,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
        is_payed BOOLEAN DEFAULT FALSE
    );
    """
    await execute(create_table_sql)

    create_function_sql = """
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """

    create_trigger_sql = """
    CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON groups
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """

    await execute(create_function_sql)
    await execute(create_trigger_sql)

async def create_purchase_history_table():
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS purchase_history (
        uid SERIAL PRIMARY KEY,
        group_id INTEGER,
        user_id BIGINT,
        price DOUBLE PRECISION,
        amount INTEGER,
        date_of_purchase TIMESTAMP WITHOUT TIME ZONE,
        paid BOOLEAN DEFAULT FALSE,
        transaction_id TEXT NOT NULL
    );
    """
    await execute(create_table_sql)
    
async def migrate_add_username_column():
    alter_table_sql = """
    ALTER TABLE users ADD COLUMN IF NOT EXISTS username TEXT;
    """
    await execute(alter_table_sql)


async def create_all_tables():
    try:
        await create_bins_table()
        await create_users_table()
        await create_groups_table()
        await create_purchase_history_table()
        await migrate_add_username_column()
        logger.info("All tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
