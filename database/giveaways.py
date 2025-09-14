from connections.database import get_connection

from services.logging import logger
import traceback, sys
import datetime
import asyncio
from modules import cache as cache_module

TableName = "giveaways"
from settings.config import BotConfigClass
BotConfig = BotConfigClass()

async def create_table():
    try:
        connection = await get_connection()

        # Table creation query
        query = f"""
        CREATE TABLE IF NOT EXISTS {TableName} (
            id SERIAL PRIMARY KEY,
            giveaway_id BIGINT NOT NULL,
            guild_id BIGINT NOT NULL,
            channel_id BIGINT,
            message_id BIGINT,
            host_id BIGINT,
            winners JSONB DEFAULT '[]',
            winner_limit INT DEFAULT 1,
            prize TEXT,
            ends_at TIMESTAMP WITH TIME ZONE,
            ended BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (giveaway_id, guild_id)
        );
        """
        await connection.execute(query)
        # Trigger function creation query
        
        trigger_function_query = f"""
        CREATE OR REPLACE FUNCTION set_giveaway_id()
        RETURNS TRIGGER AS $$
        DECLARE
            next_giveaway_id BIGINT;
        BEGIN
            -- Find the max giveaway_id for the guild_id of the new row
            SELECT COALESCE(MAX(giveaway_id), 0) + 1 INTO next_giveaway_id
            FROM {TableName}
            WHERE guild_id = NEW.guild_id;
            
            -- Set the giveaway_id to the next value
            NEW.giveaway_id = next_giveaway_id;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        await connection.execute(trigger_function_query)

        # Trigger creation with existence check
        trigger_query = f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_set_giveaway_id'
            ) THEN
                CREATE TRIGGER trigger_set_giveaway_id
                BEFORE INSERT ON {TableName}
                FOR EACH ROW
                EXECUTE FUNCTION set_giveaway_id();
            END IF;
        END $$;
        """
        await connection.execute(trigger_query)

        logger.info(f"Table {TableName} and trigger created ✅")
    except Exception as e:
        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    finally:
        await connection.close()


async def insert(
    id:int=None,
    giveaway_id:int=None,
    guild_id:int=None,
    channel_id:int=None,
    message_id:int=None,
    host_id:int=None,
    winners:list=None,
    winner_limit:int=None,
    prize:str=None,
    ends_at:str=None,
    ended:bool=None,
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
            asyncio.create_task(cache_module.giveaways_cache.update(guild_id=result['guild_id'],giveaway_id=result['giveaway_id'],data=result))
        except:
            pass
        return result
    except Exception as e:
        logger.error(f"Error inserting into table {TableName}: {e}")
    finally:
        await connection.close()

async def update(
    id:int,
    giveaway_id:int=None,
    guild_id:int=None,
    channel_id:int=None,
    message_id:int=None,
    host_id:int=None,
    winners:list=None,
    winner_limit:int=None,
    prize:str=None,
    ends_at:str=None,
    ended:bool=None,
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
            asyncio.create_task(asyncio.create_task(cache_module.giveaways_cache.update(guild_id=result['guild_id'],giveaway_id=result['giveaway_id'],data=result)))
        except:
            pass
        return result
    except Exception as e:
        logger.error(f"Error updating table {TableName}: {e}")
    finally:
        await connection.close()

async def get(
    id:int=None,
    giveaway_id:int=None,
    guild_id:int=None,
    channel_id:int=None,
    message_id:int=None,
    host_id:int=None,
    winners:list=None,
    winner_limit:int=None,
    prize:str=None,
    ends_at:str=None,
    ended:bool=None,
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
    giveaway_id:int=None,
    guild_id:int=None,
    channel_id:int=None,
    message_id:int=None,
    host_id:int=None,
    winners:list=None,
    winner_limit:int=None,
    prize:str=None,
    ends_at:str=None,
    ended:bool=None,
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
    giveaway_id:int=None,
    guild_id:int=None,
    channel_id:int=None,
    message_id:int=None,
    host_id:int=None,
    winners:list=None,
    winner_limit:int=None,
    prize:str=None,
    ends_at:str=None,
    ended:bool=None,
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
                asyncio.create_task(cache_module.giveaways_cache.delete(guild_id=r['guild_id'],giveaway_id=r['giveaway_id']))
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

