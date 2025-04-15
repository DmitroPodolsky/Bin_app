from bot.database import pool


async def execute(query: str, *args) -> int:
    conn = await pool.get_conn()
    affected_rows = 0
    try:
        affected_rows = await conn.execute(query, *args)
    except Exception as e:
        print(f"Error executing query: {e}")
    finally:
        await pool.release_conn(conn)
    return affected_rows


async def fetch(query: str, *args) -> list:
    conn = await pool.get_conn()
    result = []
    try:
        result = await conn.fetch(query, *args)
    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        await pool.release_conn(conn)
    return result


async def fetchall(query: str, *args) -> list:
    return await fetch(query, *args)


async def fetchone(query: str, *args) -> tuple:
    conn = await pool.get_conn()
    result = None
    try:
        result = await conn.fetchrow(query, *args)
    except Exception as e:
        print(f"Error fetching one row: {e}")
    finally:
        await pool.release_conn(conn)
    return result
