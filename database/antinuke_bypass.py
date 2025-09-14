from connections.database import get_connection

from services.logging import logger
import traceback, sys

import asyncio
from modules import cache as cache_module

TableName = "antinuke_bypass"
from settings.config import BotConfigClass
BotConfig = BotConfigClass()
import datetime

async def create_table():
    try:
        connection = await get_connection()

        query = f"""
        CREATE TABLE IF NOT EXISTS {TableName} (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,

            anti_channel_create BOOLEAN DEFAULT FALSE,
            
            anti_channel_delete BOOLEAN DEFAULT FALSE,
            
            anti_channel_update BOOLEAN DEFAULT FALSE,
            
            anti_role_create BOOLEAN DEFAULT FALSE,

            anti_role_delete BOOLEAN DEFAULT FALSE,

            anti_role_update BOOLEAN DEFAULT FALSE,

            anti_member_ban BOOLEAN DEFAULT FALSE,

            anti_member_unban BOOLEAN DEFAULT FALSE,

            anti_member_kick BOOLEAN DEFAULT FALSE,

            anti_member_update BOOLEAN DEFAULT FALSE,

            anti_bot_add BOOLEAN DEFAULT FALSE,

            anti_invite_delete BOOLEAN DEFAULT FALSE,

            anti_webhook_create BOOLEAN DEFAULT FALSE,

            anti_webhook_delete BOOLEAN DEFAULT FALSE,

            anti_webhook_update BOOLEAN DEFAULT FALSE,

            anti_server_update BOOLEAN DEFAULT FALSE,

            anti_emote_create BOOLEAN DEFAULT FALSE,

            anti_emote_delete BOOLEAN DEFAULT FALSE,

            anti_emote_update BOOLEAN DEFAULT FALSE,

            anti_prune_member BOOLEAN DEFAULT FALSE,

            anti_everyone_mention BOOLEAN DEFAULT FALSE,

            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(guild_id, user_id)
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
    guild_id:int=None,
    user_id:int=None, 
    anti_channel_create:bool=None,
    anti_channel_delete:bool=None,
    anti_channel_update:bool=None,
    anti_role_create:bool=None,
    anti_role_delete:bool=None,
    anti_role_update:bool=None,
    anti_member_ban:bool=None,
    anti_member_unban:bool=None,
    anti_member_kick:bool=None,
    anti_member_update:bool=None,
    anti_bot_add:bool=None,
    anti_invite_delete:bool=None,
    anti_webhook_create:bool=None,
    anti_webhook_delete:bool=None,
    anti_webhook_update:bool=None,
    anti_server_update:bool=None,
    anti_emote_create:bool=None,
    anti_emote_delete:bool=None,
    anti_emote_update:bool=None,
    anti_prune_member:bool=None,
    anti_everyone_mention:bool=None,
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
            asyncio.create_task(cache_module.antinuke_bypass_cache.update(guild_id=result['guild_id'],user_id=result['user_id'],data=result))
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
    user_id:int=None,
    anti_channel_create:bool=None,
    anti_channel_delete:bool=None,
    anti_channel_update:bool=None,
    anti_role_create:bool=None,
    anti_role_delete:bool=None,
    anti_role_update:bool=None,
    anti_member_ban:bool=None,
    anti_member_unban:bool=None,
    anti_member_kick:bool=None,
    anti_member_update:bool=None,
    anti_bot_add:bool=None,
    anti_invite_delete:bool=None,
    anti_webhook_create:bool=None,
    anti_webhook_delete:bool=None,
    anti_webhook_update:bool=None,
    anti_server_update:bool=None,
    anti_emote_create:bool=None,
    anti_emote_delete:bool=None,
    anti_emote_update:bool=None,
    anti_prune_member:bool=None,
    anti_everyone_mention:bool=None,
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
            asyncio.create_task(asyncio.create_task(cache_module.antinuke_bypass_cache.update(guild_id=result['guild_id'],user_id=result['user_id'],data=result)))
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
    user_id:int=None,
    anti_channel_create:bool=None,
    anti_channel_delete:bool=None,
    anti_channel_update:bool=None,
    anti_role_create:bool=None,
    anti_role_delete:bool=None,
    anti_role_update:bool=None,
    anti_member_ban:bool=None,
    anti_member_unban:bool=None,
    anti_member_kick:bool=None,
    anti_member_update:bool=None,
    anti_bot_add:bool=None,
    anti_invite_delete:bool=None,
    anti_webhook_create:bool=None,
    anti_webhook_delete:bool=None,
    anti_webhook_update:bool=None,
    anti_server_update:bool=None,
    anti_emote_create:bool=None,
    anti_emote_delete:bool=None,
    anti_emote_update:bool=None,
    anti_prune_member:bool=None,
    anti_everyone_mention:bool=None,
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
    user_id:int=None,
    anti_channel_create:bool=None,
    anti_channel_delete:bool=None,
    anti_channel_update:bool=None,
    anti_role_create:bool=None,
    anti_role_delete:bool=None,
    anti_role_update:bool=None,
    anti_member_ban:bool=None,
    anti_member_unban:bool=None,
    anti_member_kick:bool=None,
    anti_member_update:bool=None,
    anti_bot_add:bool=None,
    anti_invite_delete:bool=None,
    anti_webhook_create:bool=None,
    anti_webhook_delete:bool=None,
    anti_webhook_update:bool=None,
    anti_server_update:bool=None,
    anti_emote_create:bool=None,
    anti_emote_delete:bool=None,
    anti_emote_update:bool=None,
    anti_prune_member:bool=None,
    anti_everyone_mention:bool=None,
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
    user_id:int=None,
    anti_channel_create:bool=None,
    anti_channel_delete:bool=None,
    anti_channel_update:bool=None,
    anti_role_create:bool=None,
    anti_role_delete:bool=None,
    anti_role_update:bool=None,
    anti_member_ban:bool=None,
    anti_member_unban:bool=None,
    anti_member_kick:bool=None,
    anti_member_update:bool=None,
    anti_bot_add:bool=None,
    anti_invite_delete:bool=None,
    anti_webhook_create:bool=None,
    anti_webhook_delete:bool=None,
    anti_webhook_update:bool=None,
    anti_server_update:bool=None,
    anti_emote_create:bool=None,
    anti_emote_delete:bool=None,
    anti_emote_update:bool=None,
    anti_prune_member:bool=None,
    anti_everyone_mention:bool=None,
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
                asyncio.create_task(cache_module.antinuke_bypass_cache.delete(guild_id=r['guild_id'],user_id=r['user_id']))
            except Exception as e:
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