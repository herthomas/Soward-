from connections.database import get_connection

from services.logging import logger
import asyncio
import datetime

from modules import cache as cache_module

TableName = "users"
from settings.config import BotConfigClass
BotConfig = BotConfigClass()


async def create_table():
    try:
        connection = await get_connection()

        query = f"""
        CREATE TABLE IF NOT EXISTS {TableName} (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            balance FLOAT DEFAULT '0',
            level INT DEFAULT '0',
            xp INT DEFAULT '0',
            transfered_balance FLOAT DEFAULT '0',
            transfered_balance_at TIMESTAMP WITH TIME ZONE,
            received_balance FLOAT DEFAULT '0',
            received_balance_at TIMESTAMP WITH TIME ZONE,
            economy_rules_accepted BOOLEAN DEFAULT 'false',
            daily_at TIMESTAMP WITH TIME ZONE,

            type VARCHAR(255) DEFAULT 'user',
            relationship VARCHAR(255) DEFAULT 'single',
            no_prefix BOOLEAN DEFAULT 'false',
            no_prefix_subscription BOOLEAN DEFAULT 'false',
            no_prefix_end TIMESTAMP WITH TIME ZONE,
            banned BOOLEAN DEFAULT 'false',
            banned_reason TEXT,
            banned_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        );
        """
        await connection.execute(query)
        logger.info(f"Table {TableName} created ✅")
    except Exception as e:
        logger.error(f"Error creating table {TableName}: {e}")
    finally:
        await connection.close()

async def insert(
    id:int=None,
    user_id:int=None,
    balance:float=None,
    level:int=None,
    xp:int=None,
    transfered_balance:float=None,
    transfered_balance_at:str=None,
    received_balance:float=None,
    received_balance_at:str=None,
    economy_rules_accepted:bool=None,
    daily_at:str=None,
    type:str=None,
    relationship:str=None,
    no_prefix:bool=None,
    no_prefix_subscription:bool=None,
    no_prefix_end:str=None,
    banned:bool=None,
    banned_reason:str=None,
    banned_at:str=None,
    updated_at:str=None,
    created_at:str=None
):
    filtered_local = {k:v for k,v in locals().items() if v is not None}
    keys = ', '.join(filtered_local.keys())
    values = ', '.join([f"'{v}'" for v in filtered_local.values()])
    try:
        connection = await get_connection()
        query = f"""
        INSERT INTO {TableName} ({keys})
        VALUES ({values})
        RETURNING *;
        """
        result = await connection.fetchrow(query)
        try:
            asyncio.create_task(cache_module.users_cache.update(user_id=result['user_id'],data=result))
        except:
            pass
        return result
    except Exception as e:
        logger.error(f"Error inserting into table {TableName}: {e}")
    finally:
        await connection.close()

async def update(
    id:int,
    user_id:int=None,
    balance:float=None,
    level:int=None,
    xp:int=None,
    transfered_balance:float=None,
    transfered_balance_at:str=None,
    received_balance:float=None,
    received_balance_at:str=None,
    economy_rules_accepted:bool=None,
    daily_at:str=None,
    type:str=None,
    relationship:str=None,
    no_prefix:bool=None,
    no_prefix_subscription:bool=None,
    no_prefix_end:str=None,
    banned:bool=None,
    banned_reason:str=None,
    banned_at:str=None,
    updated_at:str=None,
    created_at:str=None
):
    filtered_local = {k: ('NULL' if v == '' else v) for k, v in locals().items() if v is not None}
    for key, value in filtered_local.items():
        if isinstance(value, datetime.datetime):
            filtered_local[key] = value.isoformat()  # Convert datetime to ISO 8601 string

    # Exclude 'id' from the SET clause since it should only be used in the WHERE clause
    set_values = ', '.join([f"{k} = {v!r}" if v != 'NULL' else f"{k} = NULL" for k, v in filtered_local.items() if k != 'id'])

    try:
        connection = await get_connection()
        query = f"""
        UPDATE {TableName}
        SET {set_values}
        WHERE id = '{id}'
        RETURNING *;
        """

        result = await connection.fetchrow(query)
        try:
            asyncio.create_task(cache_module.users_cache.update(user_id=result['user_id'],data=result))
        except:
            pass
        return result
    except Exception as e:
        logger.error(f"Error updating table {TableName}: {e}")
    finally:
        await connection.close()

async def get(
    id:int=None,
    user_id:int=None,
    balance:float=None,
    level:int=None,
    xp:int=None,
    transfered_balance:float=None,
    transfered_balance_at:str=None,
    received_balance:float=None,
    received_balance_at:str=None,
    economy_rules_accepted:bool=None,
    daily_at:str=None,
    type:str=None,
    relationship:str=None,
    no_prefix:bool=None,
    no_prefix_subscription:bool=None,
    no_prefix_end:str=None,
    banned:bool=None,
    banned_reason:str=None,
    banned_at:str=None,
    updated_at:str=None,
    created_at:str=None
):
    filtered_local = {k:v for k,v in locals().items() if v is not None}
    where_values = ' AND '.join([f"{k} = '{v}'" for k,v in filtered_local.items()])
    try:
        connection = await get_connection()
        query = f"""
        SELECT * FROM {TableName}
        WHERE {where_values};
        """
        result = await connection.fetchrow(query)
        return result
    except Exception as e:
        logger.error(f"Error getting from table {TableName}: {e}")
    finally:
        await connection.close()

async def gets(
    id:int=None,
    user_id:int=None,
    balance:float=None,
    level:int=None,
    xp:int=None,
    transfered_balance:float=None,
    transfered_balance_at:str=None,
    received_balance:float=None,
    received_balance_at:str=None,
    economy_rules_accepted:bool=None,
    daily_at:str=None,
    type:str=None,
    relationship:str=None,
    no_prefix:bool=None,
    no_prefix_subscription:bool=None,
    no_prefix_end:str=None,
    banned:bool=None,
    banned_reason:str=None,
    banned_at:str=None,
    updated_at:str=None,
    created_at:str=None
):
    filtered_local = {k:v for k,v in locals().items() if v is not None}
    where_values = ' AND '.join([f"{k} = '{v}'" for k,v in filtered_local.items()])
    try:
        connection = await get_connection()
        query = f"""
        SELECT * FROM {TableName}
        WHERE {where_values};
        """
        result = await connection.fetch(query)
        return result
    except Exception as e:
        logger.error(f"Error getting from table {TableName}: {e}")
    finally:
        await connection.close()

async def delete(
    id:int=None,
    user_id:int=None,
    balance:float=None,
    level:int=None,
    xp:int=None,
    transfered_balance:float=None,
    transfered_balance_at:str=None,
    received_balance:float=None,
    received_balance_at:str=None,
    economy_rules_accepted:bool=None,
    daily_at:str=None,
    type:str=None,
    relationship:str=None,
    no_prefix:bool=None,
    no_prefix_subscription:bool=None,
    no_prefix_end:str=None,
    banned:bool=None,
    banned_reason:str=None,
    banned_at:str=None,
    updated_at:str=None,
    created_at:str=None
):
    filtered_local = {k:v for k,v in locals().items() if v is not None}
    where_values = ' AND '.join([f"{k} = '{v}'" for k,v in filtered_local.items()])
    try:
        connection = await get_connection()
        query = f"""
        DELETE FROM {TableName}
        WHERE {where_values}
        RETURNING *;
        """
        result = await connection.fetch(query)
        
        for r in result:
            try:
                asyncio.create_task(cache_module.users_cache.delete(user_id=r['user_id']))
            except:
                pass
    except Exception as e:
        logger.error(f"Error deleting from table {TableName}: {e}")
    finally:
        await connection.close()

async def get_all():
    try:
        connection = await get_connection()
        query = f"""
        SELECT * FROM {TableName};
        """
        result = await connection.fetch(query)
        return result
    except Exception as e:
        logger.error(f"Error getting all from table {TableName}: {e}")
    finally:
        await connection.close()


async def add_xp(
    user_id:int,
    xp:int
):
    try:
        connection = await get_connection()
        query = f"""
        UPDATE {TableName} 
        SET xp = xp + {xp}
        WHERE user_id = '{user_id}'
        RETURNING *;
        """
        result = await connection.fetchrow(query)
        try:
            asyncio.create_task(cache_module.users_cache.update(user_id=user_id,data=result))
        except:
            pass
    except Exception as e:
        logger.error(f"Error adding xp to user {user_id}: {e}")

async def remove_xp(
    user_id:int,
    xp:int
):
    try:
        connection = await get_connection()
        query = f"""
        UPDATE {TableName} 
        SET xp = xp - {xp}
        WHERE user_id = '{user_id}'
        RETURNING *;
        """
        result = await connection.fetchrow(query)
        try:
            asyncio.create_task(cache_module.users_cache.update(user_id=user_id,data=result))
        except:
            pass
    except Exception as e:
        logger.error(f"Error removing xp from user {user_id}: {e}")

async def add_balance(
    user_id:int,
    balance:float
):
    try:
        connection = await get_connection()
        query = f"""
        UPDATE {TableName} 
        SET balance = balance + {balance}
        WHERE user_id = '{user_id}'
        RETURNING *;
        """
        result = await connection.fetchrow(query)
        try:
            asyncio.create_task(cache_module.users_cache.update(user_id=user_id,data=result))
        except:
            pass
    except Exception as e:
        logger.error(f"Error adding balance to user {user_id}: {e}")

async def remove_balance(
    user_id:int,
    balance:float
):
    try:
        connection = await get_connection()
        query = f"""
        UPDATE {TableName} 
        SET balance = balance - {balance}
        WHERE user_id = '{user_id}'
        RETURNING *;
        """
        result = await connection.fetchrow(query)
        try:
            asyncio.create_task(cache_module.users_cache.update(user_id=user_id,data=result))
        except:
            pass
    except Exception as e:
        logger.error(f"Error removing balance from user {user_id}: {e}")

