import asyncpg

from settings.config import database as databaseSettings
databaseSettings = databaseSettings()

from services.logging import logger

pool= None
async def get_connection():
    try:
        global pool
        if pool is None:
            pool = await asyncpg.create_pool(
                user=databaseSettings.user,
                password=databaseSettings.password,
                database=databaseSettings.name,
                host=databaseSettings.host,
                port=databaseSettings.port,
                min_size=1,  # Minimum number of connections in the pool
                max_size=200 # Maximum number of connections in the pool
            )
        # Use `pool.acquire()` to get a connection from the pool
        return await pool.acquire()
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

logger.info("Connected to database ✅")