import asyncpg
from loguru import logger

from bot.config import settings

pool = None


async def get_pool() -> asyncpg.Pool:
    global pool
    if pool:
        return pool
    logger.info("Creating pool...")
    pool = await asyncpg.create_pool(
        database=settings.POSTGRESS_DATABASE,
        user=settings.POSTGRESS_USER,
        password=settings.POSTGRESS_PASSWORD,
        host=settings.POSTGRESS_HOST,
        port=settings.POSTGRESS_PORT,
        min_size=5,
        max_size=20,
    )
    return pool


async def close_pool() -> bool:
    """
    Close pool
    :return: True if success else False
    """
    global pool
    try:
        if pool:
            await pool.close()
            return True
    except Exception as e:
        logger.error(f"Error closing pool: {e}")
        return False


async def get_conn() -> asyncpg.Connection:
    """
    Get connection from pool
    :return: connection
    """
    await get_pool()
    return await pool.acquire()


async def release_conn(conn: asyncpg.Connection) -> bool:
    """
    Release connection
    :param conn: connection
    :return: True if success else False
    """
    try:
        await pool.release(conn)
        return True
    except Exception as e:
        logger.error(f"Error releasing connection: {e}")
        return False
