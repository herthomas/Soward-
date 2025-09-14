from connections.database import get_connection

from services.logging import logger
import traceback, sys
import datetime
import asyncio
from modules import cache as cache_module

TableName = "welcomer_settings"
from settings.config import BotConfigClass
BotConfig = BotConfigClass()

async def create_table():
    try:
        connection = await get_connection()


        default_greet_message = r'Hello {user.mention} Welcome to {server}'
        query = f"""
        CREATE TABLE IF NOT EXISTS {TableName} (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT NOT NULL,

            welcome BOOLEAN DEFAULT FALSE,

            welcome_channel BIGINT,
            welcome_message BOOLEAN DEFAULT FALSE,
            welcome_message_content TEXT,

            welcome_embed BOOLEAN DEFAULT FALSE,
            welcome_embed_title TEXT,
            welcome_embed_description TEXT,
            welcome_embed_thumbnail TEXT,
            welcome_embed_image TEXT,
            welcome_embed_footer TEXT,
            welcome_embed_footer_icon TEXT,
            welcome_embed_color TEXT,
            welcome_embed_author TEXT,
            welcome_embed_author_icon TEXT,
            welcome_embed_author_url TEXT,

            autorole BOOLEAN DEFAULT FALSE,
            autoroles_limit INT DEFAULT 3,
            autoroles JSONB DEFAULT '[]',

            autonick BOOLEAN DEFAULT FALSE,
            autonick_format TEXT,

            greet BOOLEAN DEFAULT FALSE,
            greet_message TEXT DEFAULT '{default_greet_message}',
            greet_channels JSONB DEFAULT '[]',
            greet_delete_after INT DEFAULT 5,

            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,            
            UNIQUE(guild_id)
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
    guild_id:int=None,
    welcome:bool=None,
    welcome_channel:int=None,
    welcome_message:bool=None,
    welcome_message_content:str=None,
    welcome_embed:bool=None,
    welcome_embed_title:str=None,
    welcome_embed_description:str=None,
    welcome_embed_thumbnail:str=None,
    welcome_embed_image:str=None,
    welcome_embed_footer:str=None,
    welcome_embed_footer_icon:str=None,
    welcome_embed_color:str=None,
    welcome_embed_author:str=None,
    welcome_embed_author_icon:str=None,
    welcome_embed_author_url:str=None,
    autorole:bool=None,
    autoroles_limit:int=None,
    autoroles:str=None,
    autonick:bool=None,
    autonick_format:str=None,
    greet:bool=None,
    greet_message:str=None,
    greet_channels:list=None,
    greet_delete_after:int=None,
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
            asyncio.create_task(cache_module.guilds_welcomer_cache.update(guild_id=result['guild_id'],data=result))
        except:
            pass
        return result
    except Exception as e:
        logger.error(f"Error inserting into table {TableName}: {e}")
    finally:
        await connection.close()

async def update(
    id:int,
    guild_id:int=None,
    welcome:bool=None,
    welcome_channel:int=None,
    welcome_message:bool=None,
    welcome_message_content:str=None,
    welcome_embed:bool=None,
    welcome_embed_title:str=None,
    welcome_embed_description:str=None,
    welcome_embed_thumbnail:str=None,
    welcome_embed_image:str=None,
    welcome_embed_footer:str=None,
    welcome_embed_footer_icon:str=None,
    welcome_embed_color:str=None,
    welcome_embed_author:str=None,
    welcome_embed_author_icon:str=None,
    welcome_embed_author_url:str=None,
    autorole:bool=None,
    autoroles_limit:int=None,
    autoroles:str=None,
    autonick:bool=None,
    autonick_format:str=None,
    greet:bool=None,
    greet_message:str=None,
    greet_channels:list=None,
    greet_delete_after:int=None,
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
            asyncio.create_task(asyncio.create_task(cache_module.guilds_welcomer_cache.update(guild_id=result['guild_id'],data=result)))
        except:
            pass
        return result
    except Exception as e:
        logger.error(f"Error updating table {TableName}: {e}")
    finally:
        await connection.close()

async def get(
   id:int=None,
    guild_id:int=None,
    welcome:bool=None,
    welcome_channel:int=None,
    welcome_message:bool=None,
    welcome_message_content:str=None,
    welcome_embed:bool=None,
    welcome_embed_title:str=None,
    welcome_embed_description:str=None,
    welcome_embed_thumbnail:str=None,
    welcome_embed_image:str=None,
    welcome_embed_footer:str=None,
    welcome_embed_footer_icon:str=None,
    welcome_embed_color:str=None,
    welcome_embed_author:str=None,
    welcome_embed_author_icon:str=None,
    welcome_embed_author_url:str=None,
    autorole:bool=None,
    autoroles_limit:int=None,
    autoroles:str=None,
    autonick:bool=None,
    autonick_format:str=None,
    greet:bool=None,
    greet_message:str=None,
    greet_channels:list=None,
    greet_delete_after:int=None,
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
    guild_id:int=None,
    welcome:bool=None,
    welcome_channel:int=None,
    welcome_message:bool=None,
    welcome_message_content:str=None,
    welcome_embed:bool=None,
    welcome_embed_title:str=None,
    welcome_embed_description:str=None,
    welcome_embed_thumbnail:str=None,
    welcome_embed_image:str=None,
    welcome_embed_footer:str=None,
    welcome_embed_footer_icon:str=None,
    welcome_embed_color:str=None,
    welcome_embed_author:str=None,
    welcome_embed_author_icon:str=None,
    welcome_embed_author_url:str=None,
    autorole:bool=None,
    autoroles_limit:int=None,
    autoroles:str=None,
    autonick:bool=None,
    autonick_format:str=None,
    greet:bool=None,
    greet_message:str=None,
    greet_channels:list=None,
    greet_delete_after:int=None,
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
    guild_id:int=None,
    welcome:bool=None,
    welcome_channel:int=None,
    welcome_message:bool=None,
    welcome_message_content:str=None,
    welcome_embed:bool=None,
    welcome_embed_title:str=None,
    welcome_embed_description:str=None,
    welcome_embed_thumbnail:str=None,
    welcome_embed_image:str=None,
    welcome_embed_footer:str=None,
    welcome_embed_footer_icon:str=None,
    welcome_embed_color:str=None,
    welcome_embed_author:str=None,
    welcome_embed_author_icon:str=None,
    welcome_embed_author_url:str=None,
    autorole:bool=None,
    autoroles_limit:int=None,
    autoroles:str=None,
    autonick:bool=None,
    autonick_format:str=None,
    greet:bool=None,
    greet_message:str=None,
    greet_channels:list=None,
    greet_delete_after:int=None,
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
                asyncio.create_task(cache_module.guilds_welcomer_cache.delete(guild_id=r['guild_id']))
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

