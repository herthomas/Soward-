from connections.database import get_connection

from services.logging import logger
import datetime
import asyncio
from modules import cache as cache_module

TableName = "guilds_log"
from settings.config import BotConfigClass
BotConfig = BotConfigClass()


async def create_table():
    try:
        connection = await get_connection()

        query = f"""
        CREATE TABLE IF NOT EXISTS {TableName} (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT NOT NULL,
            enabled BOOLEAN DEFAULT FALSE,
            member_join_channel_id BIGINT,
            member_leave_channel_id BIGINT,
            member_kick_channel_id BIGINT,
            member_ban_channel_id BIGINT,
            member_unban_channel_id BIGINT,
            member_update_channel_id BIGINT,
            message_delete_channel_id BIGINT,
            message_edit_channel_id BIGINT,
            message_bulk_delete_channel_id BIGINT,
            channel_create_channel_id BIGINT,
            channel_delete_channel_id BIGINT,
            channel_update_channel_id BIGINT,
            role_create_channel_id BIGINT,
            role_delete_channel_id BIGINT,
            role_update_channel_id BIGINT,
            emoji_create_channel_id BIGINT,
            emoji_delete_channel_id BIGINT,
            emoji_update_channel_id BIGINT,
            voice_state_update_channel_id BIGINT,
            webhook_create_channel_id BIGINT,
            webhook_delete_channel_id BIGINT,
            webhook_update_channel_id BIGINT,
            invite_create_channel_id BIGINT,
            invite_delete_channel_id BIGINT,
            guild_update_channel_id BIGINT,
            antinuke_channel_id BIGINT,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(guild_id)
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
    enabled:bool=None,
    member_join_channel_id:int=None,
    member_leave_channel_id:int=None,
    member_kick_channel_id:int=None,
    member_ban_channel_id:int=None,
    member_unban_channel_id:int=None,
    member_update_channel_id:int=None,
    message_delete_channel_id:int=None,
    message_edit_channel_id:int=None,
    message_bulk_delete_channel_id:int=None,
    channel_create_channel_id:int=None,
    channel_delete_channel_id:int=None,
    channel_update_channel_id:int=None,
    role_create_channel_id:int=None,
    role_delete_channel_id:int=None,
    role_update_channel_id:int=None,
    emoji_create_channel_id:int=None,
    emoji_delete_channel_id:int=None,
    emoji_update_channel_id:int=None,
    voice_state_update_channel_id:int=None,
    webhook_create_channel_id:int=None,
    webhook_delete_channel_id:int=None,
    webhook_update_channel_id:int=None,
    invite_create_channel_id:int=None,
    invite_delete_channel_id:int=None,
    guild_update_channel_id:int=None,
    antinuke_channel_id:int=None,
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
            asyncio.create_task(cache_module.guilds_log_cache.update(guild_id=result['guild_id'],data=result))
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
    enabled:bool=None,
    member_join_channel_id:int=None,
    member_leave_channel_id:int=None,
    member_kick_channel_id:int=None,
    member_ban_channel_id:int=None,
    member_unban_channel_id:int=None,
    member_update_channel_id:int=None,
    message_delete_channel_id:int=None,
    message_edit_channel_id:int=None,
    message_bulk_delete_channel_id:int=None,
    channel_create_channel_id:int=None,
    channel_delete_channel_id:int=None,
    channel_update_channel_id:int=None,
    role_create_channel_id:int=None,
    role_delete_channel_id:int=None,
    role_update_channel_id:int=None,
    emoji_create_channel_id:int=None,
    emoji_delete_channel_id:int=None,
    emoji_update_channel_id:int=None,
    voice_state_update_channel_id:int=None,
    webhook_create_channel_id:int=None,
    webhook_delete_channel_id:int=None,
    webhook_update_channel_id:int=None,
    invite_create_channel_id:int=None,
    invite_delete_channel_id:int=None,
    guild_update_channel_id:int=None,
    antinuke_channel_id:int=None,
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
            asyncio.create_task(asyncio.create_task(cache_module.guilds_log_cache.update(guild_id=result['guild_id'],data=result)))
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
    enabled:bool=None,
    member_join_channel_id:int=None,
    member_leave_channel_id:int=None,
    member_kick_channel_id:int=None,
    member_ban_channel_id:int=None,
    member_unban_channel_id:int=None,
    member_update_channel_id:int=None,
    message_delete_channel_id:int=None,
    message_edit_channel_id:int=None,
    message_bulk_delete_channel_id:int=None,
    channel_create_channel_id:int=None,
    channel_delete_channel_id:int=None,
    channel_update_channel_id:int=None,
    role_create_channel_id:int=None,
    role_delete_channel_id:int=None,
    role_update_channel_id:int=None,
    emoji_create_channel_id:int=None,
    emoji_delete_channel_id:int=None,
    emoji_update_channel_id:int=None,
    voice_state_update_channel_id:int=None,
    webhook_create_channel_id:int=None,
    webhook_delete_channel_id:int=None,
    webhook_update_channel_id:int=None,
    invite_create_channel_id:int=None,
    invite_delete_channel_id:int=None,
    guild_update_channel_id:int=None,
    antinuke_channel_id:int=None,
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
    guild_id:int=None,
    enabled:bool=None,
    member_join_channel_id:int=None,
    member_leave_channel_id:int=None,
    member_kick_channel_id:int=None,
    member_ban_channel_id:int=None,
    member_unban_channel_id:int=None,
    member_update_channel_id:int=None,
    message_delete_channel_id:int=None,
    message_edit_channel_id:int=None,
    message_bulk_delete_channel_id:int=None,
    channel_create_channel_id:int=None,
    channel_delete_channel_id:int=None,
    channel_update_channel_id:int=None,
    role_create_channel_id:int=None,
    role_delete_channel_id:int=None,
    role_update_channel_id:int=None,
    emoji_create_channel_id:int=None,
    emoji_delete_channel_id:int=None,
    emoji_update_channel_id:int=None,
    voice_state_update_channel_id:int=None,
    webhook_create_channel_id:int=None,
    webhook_delete_channel_id:int=None,
    webhook_update_channel_id:int=None,
    invite_create_channel_id:int=None,
    invite_delete_channel_id:int=None,
    guild_update_channel_id:int=None,
    antinuke_channel_id:int=None,
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
    guild_id:int=None,
    enabled:bool=None,
    member_join_channel_id:int=None,
    member_leave_channel_id:int=None,
    member_kick_channel_id:int=None,
    member_ban_channel_id:int=None,
    member_unban_channel_id:int=None,
    member_update_channel_id:int=None,
    message_delete_channel_id:int=None,
    message_edit_channel_id:int=None,
    message_bulk_delete_channel_id:int=None,
    channel_create_channel_id:int=None,
    channel_delete_channel_id:int=None,
    channel_update_channel_id:int=None,
    role_create_channel_id:int=None,
    role_delete_channel_id:int=None,
    role_update_channel_id:int=None,
    emoji_create_channel_id:int=None,
    emoji_delete_channel_id:int=None,
    emoji_update_channel_id:int=None,
    voice_state_update_channel_id:int=None,
    webhook_create_channel_id:int=None,
    webhook_delete_channel_id:int=None,
    webhook_update_channel_id:int=None,
    invite_create_channel_id:int=None,
    invite_delete_channel_id:int=None,
    guild_update_channel_id:int=None,
    antinuke_channel_id:int=None,
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
                asyncio.create_task(cache_module.guilds_log_cache.delete(guild_id=r['guild_id']))
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