from connections.database import get_connection

from services.logging import logger
import traceback, sys
import datetime
import asyncio
from modules import cache as cache_module

TableName = "tickets"
from settings.config import BotConfigClass
BotConfig = BotConfigClass()

async def create_table():
    try:
        connection = await get_connection()

        default_embed = r'{}'

        # Table creation query
        query = f"""
        CREATE TABLE IF NOT EXISTS {TableName} (
            id SERIAL PRIMARY KEY,
            ticket_id BIGINT NOT NULL,
            ticket_module_id BIGINT NOT NULL,
            guild_id BIGINT NOT NULL,
            creator_id BIGINT,
            extra_users JSON DEFAULT '[]',
            channel_id BIGINT,
            closed BOOLEAN DEFAULT FALSE,
            deleted BOOLEAN DEFAULT FALSE,
            close_ticket_message_id BIGINT,
            closed_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticket_id,ticket_module_id,guild_id)
        );
        """
        await connection.execute(query)
        # Trigger function creation query
        trigger_function_query = f"""
        CREATE OR REPLACE FUNCTION set_ticket_id()
        RETURNS TRIGGER AS $$
        DECLARE
            next_ticket_id BIGINT;
        BEGIN
            -- Find the max ticket_id for the given ticket_module_id and guild_id
            SELECT COALESCE(MAX(ticket_id), 0) + 1 INTO next_ticket_id
            FROM {TableName}
            WHERE ticket_module_id = NEW.ticket_module_id
              AND guild_id = NEW.guild_id;
              
            -- Set the ticket_id to the next value
            NEW.ticket_id = next_ticket_id;
            
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
                SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_set_ticket_id'
            ) THEN
                CREATE TRIGGER trigger_set_ticket_id
                BEFORE INSERT ON {TableName}
                FOR EACH ROW
                EXECUTE FUNCTION set_ticket_id();
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
    ticket_id:int=None,
    ticket_module_id:int=None,
    guild_id:int=None,
    creator_id:int=None,
    extra_users:list=None,
    channel_id:int=None,
    closed:bool=None,
    deleted:bool=None,
    close_ticket_message_id:int=None,
    closed_at:str=None,
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
        return result
    except Exception as e:
        logger.error(f"Error inserting into table {TableName}: {e}")
    finally:
        await connection.close()

async def update(
    id:int,
    ticket_id:int=None,
    ticket_module_id:int=None,
    guild_id:int=None,
    creator_id:int=None,
    extra_users:list=None,
    channel_id:int=None,
    closed:bool=None,
    deleted:bool=None,
    close_ticket_message_id:int=None,
    closed_at:str=None,
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
        return result
    except Exception as e:
        logger.error(f"Error updating table {TableName}: {e}")
    finally:
        await connection.close()

async def get(
    id:int=None,
    ticket_id:int=None,
    ticket_module_id:int=None,
    guild_id:int=None,
    creator_id:int=None,
    extra_users:list=None,
    channel_id:int=None,
    closed:bool=None,
    deleted:bool=None,
    close_ticket_message_id:int=None,
    closed_at:str=None,
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
    ticket_id:int=None,
    ticket_module_id:int=None,
    guild_id:int=None,
    creator_id:int=None,
    extra_users:list=None,
    channel_id:int=None,
    closed:bool=None,
    deleted:bool=None,
    close_ticket_message_id:int=None,
    closed_at:str=None,
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
    ticket_id:int=None,
    ticket_module_id:int=None,
    guild_id:int=None,
    creator_id:int=None,
    extra_users:list=None,
    channel_id:int=None,
    closed:bool=None,
    deleted:bool=None,
    close_ticket_message_id:int=None,
    closed_at:str=None,
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


async def count(
    id:int=None,
    ticket_id:int=None,
    ticket_module_id:int=None,
    guild_id:int=None,
    creator_id:int=None,
    extra_users:list=None,
    channel_id:int=None,
    closed:bool=None,
    deleted:bool=None,
    close_ticket_message_id:int=None,
    closed_at:str=None,
    created_at:str=None
):
    filtered_local = {k:v for k,v in locals().items() if v is not None}
    where_values = ' AND '.join([f"{k} = '{v}'" for k,v in filtered_local.items()])
    try:
        connection = await get_connection()
        query = f"""
        SELECT COUNT(*) FROM {TableName}
        WHERE {where_values};
        """
        result = await connection.fetchval(query)
        return result
    except Exception as e:
        logger.error(f"Error counting from table {TableName}: {e}")
    finally:
        await connection.close()
