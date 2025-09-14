from connections.database import get_connection

from services.logging import logger
import datetime
import asyncio
from modules import cache as cache_module

TableName = "antinuke_settings"
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
            type TEXT DEFAULT 'normal',

            bypass_role_id BIGINT,

            anti_channel_create BOOLEAN DEFAULT FALSE,
            anti_channel_create_limit INT DEFAULT 1,
            anti_channel_create_punishment TEXT DEFAULT 'kick',
            
            anti_channel_delete BOOLEAN DEFAULT FALSE,
            anti_channel_delete_limit INT DEFAULT 1,
            anti_channel_delete_punishment TEXT DEFAULT 'kick',
            
            anti_channel_update BOOLEAN DEFAULT FALSE,
            anti_channel_update_limit INT DEFAULT 1,
            anti_channel_update_punishment TEXT DEFAULT 'kick',
            
            anti_role_create BOOLEAN DEFAULT FALSE,
            anti_role_create_limit INT DEFAULT 1,
            anti_role_create_punishment TEXT DEFAULT 'kick',

            anti_role_delete BOOLEAN DEFAULT FALSE,
            anti_role_delete_limit INT DEFAULT 1,
            anti_role_delete_punishment TEXT DEFAULT 'kick',

            anti_role_update BOOLEAN DEFAULT FALSE,
            anti_role_update_limit INT DEFAULT 1,
            anti_role_update_punishment TEXT DEFAULT 'kick',

            anti_member_ban BOOLEAN DEFAULT FALSE,
            anti_member_ban_limit INT DEFAULT 1,
            anti_member_ban_punishment TEXT DEFAULT 'kick',

            anti_member_unban BOOLEAN DEFAULT FALSE,
            anti_member_unban_limit INT DEFAULT 1,
            anti_member_unban_punishment TEXT DEFAULT 'kick',

            anti_member_kick BOOLEAN DEFAULT FALSE,
            anti_member_kick_limit INT DEFAULT 1,
            anti_member_kick_punishment TEXT DEFAULT 'kick',

            anti_member_update BOOLEAN DEFAULT FALSE,
            anti_member_update_limit INT DEFAULT 1,
            anti_member_update_punishment TEXT DEFAULT 'kick',

            anti_bot_add BOOLEAN DEFAULT FALSE,
            anti_bot_add_limit INT DEFAULT 1,
            anti_bot_add_punishment TEXT DEFAULT 'kick',

            anti_invite_delete BOOLEAN DEFAULT FALSE,
            anti_invite_delete_limit INT DEFAULT 1,
            anti_invite_delete_punishment TEXT DEFAULT 'kick',

            anti_webhook_create BOOLEAN DEFAULT FALSE,
            anti_webhook_create_limit INT DEFAULT 1,
            anti_webhook_create_punishment TEXT DEFAULT 'kick',

            anti_webhook_delete BOOLEAN DEFAULT FALSE,
            anti_webhook_delete_limit INT DEFAULT 1,
            anti_webhook_delete_punishment TEXT DEFAULT 'kick',

            anti_webhook_update BOOLEAN DEFAULT FALSE,
            anti_webhook_update_limit INT DEFAULT 1,
            anti_webhook_update_punishment TEXT DEFAULT 'kick',

            anti_server_update BOOLEAN DEFAULT FALSE,
            anti_server_update_limit INT DEFAULT 1,
            anti_server_update_punishment TEXT DEFAULT 'kick',

            anti_emote_create BOOLEAN DEFAULT FALSE,
            anti_emote_create_limit INT DEFAULT 1,
            anti_emote_create_punishment TEXT DEFAULT 'kick',

            anti_emote_delete BOOLEAN DEFAULT FALSE,
            anti_emote_delete_limit INT DEFAULT 1,
            anti_emote_delete_punishment TEXT DEFAULT 'kick',

            anti_emote_update BOOLEAN DEFAULT FALSE,
            anti_emote_update_limit INT DEFAULT 1,
            anti_emote_update_punishment TEXT DEFAULT 'kick',

            anti_prune_member BOOLEAN DEFAULT FALSE,
            anti_prune_member_limit INT DEFAULT 1,
            anti_prune_member_punishment TEXT DEFAULT 'kick',

            anti_everyone_mention BOOLEAN DEFAULT FALSE,
            anti_everyone_mention_limit INT DEFAULT 1,
            anti_everyone_mention_punishment TEXT DEFAULT 'mute',

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
    type:str=None,
    bypass_role_id:int=None,
    anti_channel_create:bool=None,
    anti_channel_create_limit:int=None,
    anti_channel_create_punishment:str=None,
    anti_channel_delete:bool=None,
    anti_channel_delete_limit:int=None,
    anti_channel_delete_punishment:str=None,
    anti_channel_update:bool=None,
    anti_channel_update_limit:int=None,
    anti_channel_update_punishment:str=None,
    anti_role_create:bool=None,
    anti_role_create_limit:int=None,
    anti_role_create_punishment:str=None,
    anti_role_delete:bool=None,
    anti_role_delete_limit:int=None,
    anti_role_delete_punishment:str=None,
    anti_role_update:bool=None,
    anti_role_update_limit:int=None,
    anti_role_update_punishment:str=None,
    anti_member_ban:bool=None,
    anti_member_ban_limit:int=None,
    anti_member_ban_punishment:str=None,
    anti_member_unban:bool=None,
    anti_member_unban_limit:int=None,
    anti_member_unban_punishment:str=None,
    anti_member_kick:bool=None,
    anti_member_kick_limit:int=None,
    anti_member_kick_punishment:str=None,
    anti_member_update:bool=None,
    anti_member_update_limit:int=None,
    anti_member_update_punishment:str=None,
    anti_bot_add:bool=None,
    anti_bot_add_limit:int=None,
    anti_bot_add_punishment:str=None,
    anti_invite_delete:bool=None,
    anti_invite_delete_limit:int=None,
    anti_invite_delete_punishment:str=None,
    anti_webhook_create:bool=None,
    anti_webhook_create_limit:int=None,
    anti_webhook_create_punishment:str=None,
    anti_webhook_delete:bool=None,
    anti_webhook_delete_limit:int=None,
    anti_webhook_delete_punishment:str=None,
    anti_webhook_update:bool=None,
    anti_webhook_update_limit:int=None,
    anti_webhook_update_punishment:str=None,
    anti_server_update:bool=None,
    anti_server_update_limit:int=None,
    anti_server_update_punishment:str=None,
    anti_emote_create:bool=None,
    anti_emote_create_limit:int=None,
    anti_emote_create_punishment:str=None,
    anti_emote_delete:bool=None,
    anti_emote_delete_limit:int=None,
    anti_emote_delete_punishment:str=None,
    anti_emote_update:bool=None,
    anti_emote_update_limit:int=None,
    anti_emote_update_punishment:str=None,
    anti_prune_member:bool=None,
    anti_prune_member_limit:int=None,
    anti_prune_member_punishment:str=None,
    anti_everyone_mention:bool=None,
    anti_everyone_mention_limit:int=None,
    anti_everyone_mention_punishment:str=None,
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
            asyncio.create_task(cache_module.antinuke_settings_cache.update(guild_id=result['guild_id'],data=result))
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
    type:str=None,
    bypass_role_id:int=None,
    anti_channel_create:bool=None,
    anti_channel_create_limit:int=None,
    anti_channel_create_punishment:str=None,
    anti_channel_delete:bool=None,
    anti_channel_delete_limit:int=None,
    anti_channel_delete_punishment:str=None,
    anti_channel_update:bool=None,
    anti_channel_update_limit:int=None,
    anti_channel_update_punishment:str=None,
    anti_role_create:bool=None,
    anti_role_create_limit:int=None,
    anti_role_create_punishment:str=None,
    anti_role_delete:bool=None,
    anti_role_delete_limit:int=None,
    anti_role_delete_punishment:str=None,
    anti_role_update:bool=None,
    anti_role_update_limit:int=None,
    anti_role_update_punishment:str=None,
    anti_member_ban:bool=None,
    anti_member_ban_limit:int=None,
    anti_member_ban_punishment:str=None,
    anti_member_unban:bool=None,
    anti_member_unban_limit:int=None,
    anti_member_unban_punishment:str=None,
    anti_member_kick:bool=None,
    anti_member_kick_limit:int=None,
    anti_member_kick_punishment:str=None,
    anti_member_update:bool=None,
    anti_member_update_limit:int=None,
    anti_member_update_punishment:str=None,
    anti_bot_add:bool=None,
    anti_bot_add_limit:int=None,
    anti_bot_add_punishment:str=None,
    anti_invite_delete:bool=None,
    anti_invite_delete_limit:int=None,
    anti_invite_delete_punishment:str=None,
    anti_webhook_create:bool=None,
    anti_webhook_create_limit:int=None,
    anti_webhook_create_punishment:str=None,
    anti_webhook_delete:bool=None,
    anti_webhook_delete_limit:int=None,
    anti_webhook_delete_punishment:str=None,
    anti_webhook_update:bool=None,
    anti_webhook_update_limit:int=None,
    anti_webhook_update_punishment:str=None,
    anti_server_update:bool=None,
    anti_server_update_limit:int=None,
    anti_server_update_punishment:str=None,
    anti_emote_create:bool=None,
    anti_emote_create_limit:int=None,
    anti_emote_create_punishment:str=None,
    anti_emote_delete:bool=None,
    anti_emote_delete_limit:int=None,
    anti_emote_delete_punishment:str=None,
    anti_emote_update:bool=None,
    anti_emote_update_limit:int=None,
    anti_emote_update_punishment:str=None,
    anti_prune_member:bool=None,
    anti_prune_member_limit:int=None,
    anti_prune_member_punishment:str=None,
    anti_everyone_mention:bool=None,
    anti_everyone_mention_limit:int=None,
    anti_everyone_mention_punishment:str=None,
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
            asyncio.create_task(asyncio.create_task(cache_module.antinuke_settings_cache.update(guild_id=result['guild_id'],data=result)))
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
    type:str=None,
    bypass_role_id:int=None,
    anti_channel_create:bool=None,
    anti_channel_create_limit:int=None,
    anti_channel_create_punishment:str=None,
    anti_channel_delete:bool=None,
    anti_channel_delete_limit:int=None,
    anti_channel_delete_punishment:str=None,
    anti_channel_update:bool=None,
    anti_channel_update_limit:int=None,
    anti_channel_update_punishment:str=None,
    anti_role_create:bool=None,
    anti_role_create_limit:int=None,
    anti_role_create_punishment:str=None,
    anti_role_delete:bool=None,
    anti_role_delete_limit:int=None,
    anti_role_delete_punishment:str=None,
    anti_role_update:bool=None,
    anti_role_update_limit:int=None,
    anti_role_update_punishment:str=None,
    anti_member_ban:bool=None,
    anti_member_ban_limit:int=None,
    anti_member_ban_punishment:str=None,
    anti_member_unban:bool=None,
    anti_member_unban_limit:int=None,
    anti_member_unban_punishment:str=None,
    anti_member_kick:bool=None,
    anti_member_kick_limit:int=None,
    anti_member_kick_punishment:str=None,
    anti_member_update:bool=None,
    anti_member_update_limit:int=None,
    anti_member_update_punishment:str=None,
    anti_bot_add:bool=None,
    anti_bot_add_limit:int=None,
    anti_bot_add_punishment:str=None,
    anti_invite_delete:bool=None,
    anti_invite_delete_limit:int=None,
    anti_invite_delete_punishment:str=None,
    anti_webhook_create:bool=None,
    anti_webhook_create_limit:int=None,
    anti_webhook_create_punishment:str=None,
    anti_webhook_delete:bool=None,
    anti_webhook_delete_limit:int=None,
    anti_webhook_delete_punishment:str=None,
    anti_webhook_update:bool=None,
    anti_webhook_update_limit:int=None,
    anti_webhook_update_punishment:str=None,
    anti_server_update:bool=None,
    anti_server_update_limit:int=None,
    anti_server_update_punishment:str=None,
    anti_emote_create:bool=None,
    anti_emote_create_limit:int=None,
    anti_emote_create_punishment:str=None,
    anti_emote_delete:bool=None,
    anti_emote_delete_limit:int=None,
    anti_emote_delete_punishment:str=None,
    anti_emote_update:bool=None,
    anti_emote_update_limit:int=None,
    anti_emote_update_punishment:str=None,
    anti_prune_member:bool=None,
    anti_prune_member_limit:int=None,
    anti_prune_member_punishment:str=None,
    anti_everyone_mention:bool=None,
    anti_everyone_mention_limit:int=None,
    anti_everyone_mention_punishment:str=None,
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
    type:str=None,
    bypass_role_id:int=None,
    anti_channel_create:bool=None,
    anti_channel_create_limit:int=None,
    anti_channel_create_punishment:str=None,
    anti_channel_delete:bool=None,
    anti_channel_delete_limit:int=None,
    anti_channel_delete_punishment:str=None,
    anti_channel_update:bool=None,
    anti_channel_update_limit:int=None,
    anti_channel_update_punishment:str=None,
    anti_role_create:bool=None,
    anti_role_create_limit:int=None,
    anti_role_create_punishment:str=None,
    anti_role_delete:bool=None,
    anti_role_delete_limit:int=None,
    anti_role_delete_punishment:str=None,
    anti_role_update:bool=None,
    anti_role_update_limit:int=None,
    anti_role_update_punishment:str=None,
    anti_member_ban:bool=None,
    anti_member_ban_limit:int=None,
    anti_member_ban_punishment:str=None,
    anti_member_unban:bool=None,
    anti_member_unban_limit:int=None,
    anti_member_unban_punishment:str=None,
    anti_member_kick:bool=None,
    anti_member_kick_limit:int=None,
    anti_member_kick_punishment:str=None,
    anti_member_update:bool=None,
    anti_member_update_limit:int=None,
    anti_member_update_punishment:str=None,
    anti_bot_add:bool=None,
    anti_bot_add_limit:int=None,
    anti_bot_add_punishment:str=None,
    anti_invite_delete:bool=None,
    anti_invite_delete_limit:int=None,
    anti_invite_delete_punishment:str=None,
    anti_webhook_create:bool=None,
    anti_webhook_create_limit:int=None,
    anti_webhook_create_punishment:str=None,
    anti_webhook_delete:bool=None,
    anti_webhook_delete_limit:int=None,
    anti_webhook_delete_punishment:str=None,
    anti_webhook_update:bool=None,
    anti_webhook_update_limit:int=None,
    anti_webhook_update_punishment:str=None,
    anti_server_update:bool=None,
    anti_server_update_limit:int=None,
    anti_server_update_punishment:str=None,
    anti_emote_create:bool=None,
    anti_emote_create_limit:int=None,
    anti_emote_create_punishment:str=None,
    anti_emote_delete:bool=None,
    anti_emote_delete_limit:int=None,
    anti_emote_delete_punishment:str=None,
    anti_emote_update:bool=None,
    anti_emote_update_limit:int=None,
    anti_emote_update_punishment:str=None,
    anti_prune_member:bool=None,
    anti_prune_member_limit:int=None,
    anti_prune_member_punishment:str=None,
    anti_everyone_mention:bool=None,
    anti_everyone_mention_limit:int=None,
    anti_everyone_mention_punishment:str=None,
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
    type:str=None,
    bypass_role_id:int=None,
    anti_channel_create:bool=None,
    anti_channel_create_limit:int=None,
    anti_channel_create_punishment:str=None,
    anti_channel_delete:bool=None,
    anti_channel_delete_limit:int=None,
    anti_channel_delete_punishment:str=None,
    anti_channel_update:bool=None,
    anti_channel_update_limit:int=None,
    anti_channel_update_punishment:str=None,
    anti_role_create:bool=None,
    anti_role_create_limit:int=None,
    anti_role_create_punishment:str=None,
    anti_role_delete:bool=None,
    anti_role_delete_limit:int=None,
    anti_role_delete_punishment:str=None,
    anti_role_update:bool=None,
    anti_role_update_limit:int=None,
    anti_role_update_punishment:str=None,
    anti_member_ban:bool=None,
    anti_member_ban_limit:int=None,
    anti_member_ban_punishment:str=None,
    anti_member_unban:bool=None,
    anti_member_unban_limit:int=None,
    anti_member_unban_punishment:str=None,
    anti_member_kick:bool=None,
    anti_member_kick_limit:int=None,
    anti_member_kick_punishment:str=None,
    anti_member_update:bool=None,
    anti_member_update_limit:int=None,
    anti_member_update_punishment:str=None,
    anti_bot_add:bool=None,
    anti_bot_add_limit:int=None,
    anti_bot_add_punishment:str=None,
    anti_invite_delete:bool=None,
    anti_invite_delete_limit:int=None,
    anti_invite_delete_punishment:str=None,
    anti_webhook_create:bool=None,
    anti_webhook_create_limit:int=None,
    anti_webhook_create_punishment:str=None,
    anti_webhook_delete:bool=None,
    anti_webhook_delete_limit:int=None,
    anti_webhook_delete_punishment:str=None,
    anti_webhook_update:bool=None,
    anti_webhook_update_limit:int=None,
    anti_webhook_update_punishment:str=None,
    anti_server_update:bool=None,
    anti_server_update_limit:int=None,
    anti_server_update_punishment:str=None,
    anti_emote_create:bool=None,
    anti_emote_create_limit:int=None,
    anti_emote_create_punishment:str=None,
    anti_emote_delete:bool=None,
    anti_emote_delete_limit:int=None,
    anti_emote_delete_punishment:str=None,
    anti_emote_update:bool=None,
    anti_emote_update_limit:int=None,
    anti_emote_update_punishment:str=None,
    anti_prune_member:bool=None,
    anti_prune_member_limit:int=None,
    anti_prune_member_punishment:str=None,
    anti_everyone_mention:bool=None,
    anti_everyone_mention_limit:int=None,
    anti_everyone_mention_punishment:str=None,
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
                asyncio.create_task(cache_module.antinuke_settings_cache.delete(guild_id=r['guild_id']))
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


async def change_antinuke_settings_type(cache_antinuke_settings:dict,new_type:str):
    new_type = new_type.lower()
    if new_type not in ['normal','extream','custom']:
        return logger.warning(f"Invalid type {new_type} is choosen by the user for the guild {cache_antinuke_settings.get('guild_id')}")
    if new_type == 'custom':
        return logger.info(f"Custom settings is choosen by the user.")
    if new_type == 'normal':
        await update(
            id=cache_antinuke_settings.get('id'),

            anti_channel_create=True,
            anti_channel_create_limit=3,
            anti_channel_create_punishment="kick",

            anti_channel_delete=True,
            anti_channel_delete_limit=3,
            anti_channel_delete_punishment="kick",

            anti_channel_update=True,
            anti_channel_update_limit=3,
            anti_channel_update_punishment="kick",

            anti_role_create=True,
            anti_role_create_limit=3,
            anti_role_create_punishment="kick",

            anti_role_delete=True,
            anti_role_delete_limit=3,
            anti_role_delete_punishment="kick",

            anti_role_update=True,
            anti_role_update_limit=3,
            anti_role_update_punishment="kick",

            anti_member_ban=True,
            anti_member_ban_limit=3,
            anti_member_ban_punishment="kick",

            anti_member_unban=True,
            anti_member_unban_limit=3,
            anti_member_unban_punishment="kick",

            anti_member_kick=True,
            anti_member_kick_limit=3,
            anti_member_kick_punishment="kick",

            anti_member_update=True,
            anti_member_update_limit=3,
            anti_member_update_punishment="kick",

            anti_bot_add=True,
            anti_bot_add_limit=2,
            anti_bot_add_punishment="kick",

            anti_invite_delete=True,
            anti_invite_delete_limit=3,
            anti_invite_delete_punishment="kick",

            anti_webhook_create=True,
            anti_webhook_create_limit=3,
            anti_webhook_create_punishment="kick",

            anti_webhook_update=True,
            anti_webhook_update_limit=3,
            anti_webhook_update_punishment="kick",

            anti_server_update=True,
            anti_server_update_limit=3,
            anti_server_update_punishment="kick",

            anti_emote_create=True,
            anti_emote_create_limit=3,
            anti_emote_create_punishment="kick",

            anti_emote_delete=True,
            anti_emote_delete_limit=3,
            anti_emote_delete_punishment="kick",

            anti_emote_update=True,
            anti_emote_update_limit=3,
            anti_emote_update_punishment="kick",

            anti_prune_member=True,
            anti_prune_member_limit=3,
            anti_prune_member_punishment="kick",

            anti_everyone_mention=True,
            anti_everyone_mention_limit=1,
            anti_everyone_mention_punishment="mute"
        )
        return logger.info(f"Normal settings is choosen by the user for the guild {cache_antinuke_settings.get('guild_id')}")
    if new_type == 'extream':
        # all limit will be 1 and puishment will be ban
        await update(
            id=cache_antinuke_settings.get('id'),

            anti_channel_create=True,
            anti_channel_create_limit=1,
            anti_channel_create_punishment="ban",

            anti_channel_delete=True,
            anti_channel_delete_limit=1,
            anti_channel_delete_punishment="ban",

            anti_channel_update=True,
            anti_channel_update_limit=1,
            anti_channel_update_punishment="ban",

            anti_role_create=True,
            anti_role_create_limit=1,
            anti_role_create_punishment="ban",

            anti_role_delete=True,
            anti_role_delete_limit=1,
            anti_role_delete_punishment="ban",

            anti_role_update=True,
            anti_role_update_limit=1,
            anti_role_update_punishment="ban",

            anti_member_ban=True,
            anti_member_ban_limit=1,
            anti_member_ban_punishment="ban",

            anti_member_unban=True,
            anti_member_unban_limit=1,
            anti_member_unban_punishment="ban",

            anti_member_kick=True,
            anti_member_kick_limit=1,
            anti_member_kick_punishment="ban",

            anti_member_update=True,
            anti_member_update_limit=1,
            anti_member_update_punishment="ban",

            anti_bot_add=True,
            anti_bot_add_limit=1,
            anti_bot_add_punishment="ban",

            anti_invite_delete=True,
            anti_invite_delete_limit=1,
            anti_invite_delete_punishment="ban",

            anti_webhook_create=True,
            anti_webhook_create_limit=1,
            anti_webhook_create_punishment="ban",

            anti_webhook_update=True,
            anti_webhook_update_limit=1,
            anti_webhook_update_punishment="ban",

            anti_server_update=True,
            anti_server_update_limit=1,
            anti_server_update_punishment="ban",

            anti_emote_create=True,
            anti_emote_create_limit=1,
            anti_emote_create_punishment="ban",

            anti_emote_delete=True,
            anti_emote_delete_limit=1,
            anti_emote_delete_punishment="ban",

            anti_emote_update=True,
            anti_emote_update_limit=1,
            anti_emote_update_punishment="ban",

            anti_prune_member=True,
            anti_prune_member_limit=1,
            anti_prune_member_punishment="ban",

            anti_everyone_mention=True,
            anti_everyone_mention_limit=1,
            anti_everyone_mention_punishment="kick"
        )
        return logger.info(f"Extream settings is choosen by the user for the guild {cache_antinuke_settings.get('guild_id')}")
    