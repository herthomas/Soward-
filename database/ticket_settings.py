from connections.database import get_connection

from services.logging import logger
import traceback, sys
import datetime
import asyncio
from modules import cache as cache_module

TableName = "ticket_settings"
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
            ticket_module_id BIGINT NOT NULL,
            enabled BOOLEAN DEFAULT FALSE,
            guild_id BIGINT NOT NULL,
            support_roles JSON DEFAULT '[]',
            ticket_limit INT DEFAULT 1,
            open_ticket_category_id BIGINT,
            closed_ticket_category_id BIGINT,
            ticket_panel_channel_id BIGINT,
            ticket_panel_message_id BIGINT,
            ticket_panel_message_content TEXT,
            ticket_panel_message_embed JSON DEFAULT '{default_embed}',
            close_ticket_message_content TEXT,
            close_ticket_message_embed JSON DEFAULT '{default_embed}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticket_module_id, guild_id)
        );
        """
        await connection.execute(query)

        # Trigger function creation query
        trigger_function_query = f"""
        CREATE OR REPLACE FUNCTION set_ticket_module_id()
        RETURNS TRIGGER AS $$
        DECLARE
            next_ticket_module_id BIGINT;
        BEGIN
            -- Find the max ticket_module_id for the guild_id of the new row
            SELECT COALESCE(MAX(ticket_module_id), 0) + 1 INTO next_ticket_module_id
            FROM {TableName}
            WHERE guild_id = NEW.guild_id;
            
            -- Set the ticket_module_id to the next value
            NEW.ticket_module_id = next_ticket_module_id;
            
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
                SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_set_ticket_module_id'
            ) THEN
                CREATE TRIGGER trigger_set_ticket_module_id
                BEFORE INSERT ON {TableName}
                FOR EACH ROW
                EXECUTE FUNCTION set_ticket_module_id();
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
    ticket_module_id:int=None,
    enabled:bool=None,
    guild_id:int=None,
    support_roles:list=None,
    ticket_limit:int=None,
    open_ticket_category_id:int=None,
    closed_ticket_category_id:int=None,
    ticket_panel_channel_id:int=None,
    ticket_panel_message_id:int=None,
    ticket_panel_message_content:str=None,
    ticket_panel_message_embed:dict=None,
    close_ticket_message_content:str=None,
    close_ticket_message_embed:dict=None,
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
            asyncio.create_task(cache_module.ticket_settings_cache.update(guild_id=result['guild_id'],ticket_module_id=result['ticket_module_id'],data=result))
        except:
            pass
        return result
    except Exception as e:
        logger.error(f"Error inserting into table {TableName}: {e}")
    finally:
        await connection.close()

async def update(
    id:int,
    ticket_module_id:int=None,
    enabled:bool=None,
    guild_id:int=None,
    support_roles:list=None,
    ticket_limit:int=None,
    open_ticket_category_id:int=None,
    closed_ticket_category_id:int=None,
    ticket_panel_channel_id:int=None,
    ticket_panel_message_id:int=None,
    ticket_panel_message_content:str=None,
    ticket_panel_message_embed:dict=None,
    close_ticket_message_content:str=None,
    close_ticket_message_embed:dict=None,
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
            asyncio.create_task(asyncio.create_task(cache_module.ticket_settings_cache.update(guild_id=result['guild_id'],ticket_module_id=result['ticket_module_id'],data=result)))
        except:
            pass
        return result
    except Exception as e:
        logger.error(f"Error updating table {TableName}: {e}")
    finally:
        await connection.close()

async def get(
    id:int=None,
    ticket_module_id:int=None,
    enabled:bool=None,
    guild_id:int=None,
    support_roles:list=None,
    ticket_limit:int=None,
    open_ticket_category_id:int=None,
    closed_ticket_category_id:int=None,
    ticket_panel_channel_id:int=None,
    ticket_panel_message_id:int=None,
    ticket_panel_message_content:str=None,
    ticket_panel_message_embed:dict=None,
    close_ticket_message_content:str=None,
    close_ticket_message_embed:dict=None,
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
    ticket_module_id:int=None,
    enabled:bool=None,
    guild_id:int=None,
    support_roles:list=None,
    ticket_limit:int=None,
    open_ticket_category_id:int=None,
    closed_ticket_category_id:int=None,
    ticket_panel_channel_id:int=None,
    ticket_panel_message_id:int=None,
    ticket_panel_message_content:str=None,
    ticket_panel_message_embed:dict=None,
    close_ticket_message_content:str=None,
    close_ticket_message_embed:dict=None,
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
    ticket_module_id:int=None,
    enabled:bool=None,
    guild_id:int=None,
    support_roles:list=None,
    ticket_limit:int=None,
    open_ticket_category_id:int=None,
    closed_ticket_category_id:int=None,
    ticket_panel_channel_id:int=None,
    ticket_panel_message_id:int=None,
    ticket_panel_message_content:str=None,
    ticket_panel_message_embed:dict=None,
    close_ticket_message_content:str=None,
    close_ticket_message_embed:dict=None,
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
                asyncio.create_task(cache_module.ticket_settings_cache.delete(guild_id=r['guild_id'],ticket_module_id=r['ticket_module_id']))
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


