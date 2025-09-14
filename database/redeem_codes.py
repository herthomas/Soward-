from connections.database import get_connection

from services.logging import logger
import traceback, sys
import datetime
import asyncio
from modules import cache as cache_module

TableName = "redeem_codes"
from settings.config import BotConfigClass
BotConfig = BotConfigClass()


async def create_table():
    try:
        connection = await get_connection()

        # add a validation which will be added to the redeemed product how many day the subscription will be valid
        query = f"""
        CREATE TABLE IF NOT EXISTS {TableName} (
            id SERIAL PRIMARY KEY,
            code TEXT NOT NULL,
            code_type TEXT NOT NULL,
            code_value TEXT NOT NULL,
            valid_for_days INT,
            expires_at TIMESTAMP WITH TIME ZONE,
            claimed BOOLEAN DEFAULT FALSE,
            claimed_by BIGINT,
            claimed_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,            
            UNIQUE(code)
        );
        """
        await connection.execute(query)
        logger.info(f"Table {TableName} created ✅")
    except Exception as e:
        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    finally:
        await connection.close()


async def insert(
    id:int=None,
    code:str=None,
    code_type:str=None,
    code_value:str=None,
    valid_for_days:int=None,
    expires_at:str=None,
    claimed:bool=None,
    claimed_by:int=None,
    claimed_at:str=None,
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
            asyncio.create_task(cache_module.redeem_codes_cache.update(code=result['code'],data=result))
        except:
            pass
        return result
    except Exception as e:
        logger.error(f"Error inserting into table {TableName}: {e}")
    finally:
        await connection.close()

async def update(
    id:int,
    code:str=None,
    code_type:str=None,
    code_value:str=None,
    valid_for_days:int=None,
    expires_at:str=None,
    claimed:bool=None,
    claimed_by:int=None,
    claimed_at:str=None,
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
            asyncio.create_task(asyncio.create_task(cache_module.redeem_codes_cache.update(code=result['code'],data=result)))
        except:
            pass
        return result
    except Exception as e:
        logger.error(f"Error updating table {TableName}: {e}")
    finally:
        await connection.close()

async def get(
    id:int=None,
    code:str=None,
    code_type:str=None,
    code_value:str=None,
    valid_for_days:int=None,
    expires_at:str=None,
    claimed:bool=None,
    claimed_by:int=None,
    claimed_at:str=None,
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
    code:str=None,
    code_type:str=None,
    code_value:str=None,
    valid_for_days:int=None,
    expires_at:str=None,
    claimed:bool=None,
    claimed_by:int=None,
    claimed_at:str=None,
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
    code:str=None,
    code_type:str=None,
    code_value:str=None,
    valid_for_days:int=None,
    expires_at:str=None,
    claimed:bool=None,
    claimed_by:int=None,
    claimed_at:str=None,
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
                asyncio.create_task(cache_module.redeem_codes_cache.delete(code=r['code']))
            except:
                pass
        return result
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


