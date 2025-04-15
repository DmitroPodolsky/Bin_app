from bot.database.sql_operations import execute, fetchall, fetchone


async def create_bin(
    id: int,
    country: str,
    bank: str,
    brand: str,
    type: str,
    level: str
):
    """
    Inserts a new bin into the 'bins' table.
    """
    insert_sql = """
    INSERT INTO bins (id, country, bank, brand, type, level)
    VALUES ($1, $2, $3, $4, $5, $6)
    ON CONFLICT (id) DO NOTHING;
    """
    await execute(insert_sql, id, country, bank, brand, type, level)
    
async def get_bin(
    id: int
):
    """
    Fetches a bin from the 'bins' table.
    """
    select_sql = """
    SELECT * FROM bins WHERE id = $1;
    """
    row = await fetchone(select_sql, id)
    return row

async def filter_bins(
    country: str = None,
    bank: str = None,
    brand: str = None,
    type: str = None,
    level: str = None
):
    """
    Fetches bins from the 'bins' table based on filters.
    """
    filter_sql = """
    SELECT * FROM bins WHERE
        ($1 IS NULL OR country = $1) AND
        ($2 IS NULL OR bank = $2) AND
        ($3 IS NULL OR brand = $3) AND
        ($4 IS NULL OR type = $4) AND
        ($5 IS NULL OR level = $5);
    """
    
    rows = await fetchall(filter_sql, country, bank, brand, type, level)
    return rows


async def create_user(
    user_id: int,
):
    """
    Inserts a new user into the 'users' table.
    """
    sql_query = """
    INSERT INTO users (id)
    VALUES ($1)
    ON CONFLICT (id) DO NOTHING;
    """
    
    await execute(sql_query, user_id)
    
async def set_user_admin(
    user_id: int,
):
    """
    Sets a user as an admin in the 'users' table.
    """
    sql_query = """
    UPDATE users
    SET is_admin = TRUE
    WHERE id = $1;
    """
    
    await execute(sql_query, user_id)
    
async def get_users():
    sql_query = """
    SELECT * FROM users;
    """
    rows = await fetchall(sql_query)
    return rows
    
async def create_group(
    group_id: int,
    owner_id: int,
    owner_username: str,
):
    sql_query = """
    INSERT INTO groups (id, owner_id, owner_username)
    VALUES ($1, $2, $3)
    """
    await execute(sql_query, group_id, owner_id, owner_username)
    
async def get_group(id: int):
    sql_query = """
    SELECT * FROM groups WHERE id = $1;
    """
    row = await fetchone(sql_query, id)
    return row

async def get_groups():
    sql_query = """
    SELECT * FROM groups;
    """
    rows = await fetchall(sql_query)
    return rows
    
async def increase_group_bins(
    group_id: int,
):
    sql_query = """
    UPDATE groups
    SET count_collected_bins = count_collected_bins + 1
    WHERE id = $1;
    """
    await execute(sql_query, group_id)
    
async def set_group_payed(
    group_id: int,
):
    sql_query = """
    UPDATE groups
    SET is_payed = TRUE
    WHERE id = $1;
    """
    await execute(sql_query, group_id)

async def get_user(
    user_id: int
):
    sql_query = """
    SELECT id, is_admin FROM users WHERE id = $1;
    """
    
    row = await fetchone(sql_query, user_id)
    return row

async def increase_user_bins(
    user_id: int,
):
    sql_query = """
    UPDATE users
    SET count_collected_bins = count_collected_bins + 1
    WHERE id = $1;
    """
    
    await execute(sql_query, user_id)
    
async def add_purchase_history(group_id: int, user_id: int, price: float, amount: int, district_id: int, transaction_id: str) -> None:
    sql_query = """
    INSERT INTO purchase_history (group_id, user_id, price, amount, date_of_purchase, paid, transaction_id)
    VALUES ($1, $2, $3, $4, NOW(), FALSE, $5);
    """
    await execute(sql_query, group_id, user_id, price, amount, transaction_id)
    
    
async def get_user_purchase_histories_user(
    user_id: int
):
    sql_query = """
    SELECT * FROM purchase_history WHERE user_id = $1;
    """
    
    rows = await fetchall(sql_query, user_id)
    return rows

async def get_user_purchase_histories_group(
    group_id: int
):
    sql_query = """
    SELECT * FROM purchase_history WHERE group_id = $1;
    """
    
    rows = await fetchall(sql_query, group_id)
    return rows
    
async def get_count_of_bins():
    sql_query = """
    SELECT COUNT(*) FROM bins;
    """
    
    row = await fetchone(sql_query)
    return row[0]