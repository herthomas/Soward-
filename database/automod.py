from connections.database import get_connection

from services.logging import logger
import traceback, sys
import datetime
import asyncio
from modules import cache as cache_module
import json

TableName = "automod"
from settings.config import BotConfigClass
BotConfig = BotConfigClass()

async def create_table():
    try:
        connection = await get_connection()

        query = f"""
        CREATE TABLE IF NOT EXISTS {TableName} (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT,

            antilink_enabled BOOLEAN DEFAULT FALSE,
            antilink_rule_id BIGINT,
            antilink_whitelist_roles JSON DEFAULT '[]',
            antilink_whitelist_channels JSON DEFAULT '[]',

            antispam_enabled BOOLEAN DEFAULT FALSE,
            antispam_whitelist_roles JSON DEFAULT '[]',
            antispam_whitelist_channels JSON DEFAULT '[]',
            antispam_max_messages INT DEFAULT 10,
            antispam_max_interval INT DEFAULT 30,
            antispam_max_mentions INT DEFAULT 5,
            antispam_max_emojis INT DEFAULT 10,
            antispam_max_caps INT DEFAULT 50,
            antispam_punishment TEXT DEFAULT 'mute',
            antispam_punishment_duration INT DEFAULT 10,

            antibadwords_enabled BOOLEAN DEFAULT FALSE,
            antibadwords_rule_id BIGINT,
            antibadwords_whitelist_roles JSON DEFAULT '[]',
            antibadwords_whitelist_channels JSON DEFAULT '[]',
            antibadwords_words JSON DEFAULT '[]',

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
    antilink_enabled:bool=None,
    antilink_rule_id:int=None,
    antilink_whitelist_roles:list=None,
    antilink_whitelist_channels:list=None,
    antispam_enabled:bool=None,
    antispam_whitelist_roles:list=None,
    antispam_whitelist_channels:list=None,
    antispam_max_messages:int=None,
    antispam_max_interval:int=None,
    antispam_max_mentions:int=None,
    antispam_max_emojis:int=None,
    antispam_max_caps:int=None,
    antispam_punishment:str=None,
    antispam_punishment_duration:int=None,
    antibadwords_enabled:bool=None,
    antibadwords_rule_id:int=None,
    antibadwords_whitelist_roles:list=None,
    antibadwords_whitelist_channels:list=None,
    antibadwords_words:list=None,
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
            asyncio.create_task(cache_module.automod_cache.update(guild_id=result['guild_id'],data=result))
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
    antilink_enabled:bool=None,
    antilink_rule_id:int=None,
    antilink_whitelist_roles:list=None,
    antilink_whitelist_channels:list=None,
    antispam_enabled:bool=None,
    antispam_whitelist_roles:list=None,
    antispam_whitelist_channels:list=None,
    antispam_max_messages:int=None,
    antispam_max_interval:int=None,
    antispam_max_mentions:int=None,
    antispam_max_emojis:int=None,
    antispam_max_caps:int=None,
    antispam_punishment:str=None,
    antispam_punishment_duration:int=None,
    antibadwords_enabled:bool=None,
    antibadwords_rule_id:int=None,
    antibadwords_whitelist_roles:list=None,
    antibadwords_whitelist_channels:list=None,
    antibadwords_words:list=None,
    created_at:str=None
):
    filtered_local = {k: ('NULL' if v == '' else v) for k, v in locals().items() if v is not None}
    for key, value in filtered_local.items():
        if isinstance(value, datetime.datetime):
            filtered_local[key] = value.isoformat()  # Convert datetime to ISO 8601 string
        elif isinstance(value, list):
            filtered_local[key] = json.dumps(value)
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
            asyncio.create_task(asyncio.create_task(cache_module.automod_cache.update(guild_id=result['guild_id'],data=result)))
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
    antilink_enabled:bool=None,
    antilink_rule_id:int=None,
    antilink_whitelist_roles:list=None,
    antilink_whitelist_channels:list=None,
    antispam_enabled:bool=None,
    antispam_whitelist_roles:list=None,
    antispam_whitelist_channels:list=None,
    antispam_max_messages:int=None,
    antispam_max_interval:int=None,
    antispam_max_mentions:int=None,
    antispam_max_emojis:int=None,
    antispam_max_caps:int=None,
    antispam_punishment:str=None,
    antispam_punishment_duration:int=None,
    antibadwords_enabled:bool=None,
    antibadwords_rule_id:int=None,
    antibadwords_whitelist_roles:list=None,
    antibadwords_whitelist_channels:list=None,
    antibadwords_words:list=None,
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
        try:
            asyncio.create_task(cache_module.automod_cache.update(guild_id=result['guild_id'],data=result))
        except:
            pass
        return result
    except Exception as e:
        logger.error(f"Error getting from table {TableName}: {e}")
    finally:
        await connection.close()

async def gets(
    id:int=None,
    guild_id:int=None,
    antilink_enabled:bool=None,
    antilink_rule_id:int=None,
    antilink_whitelist_roles:list=None,
    antilink_whitelist_channels:list=None,
    antispam_enabled:bool=None,
    antispam_whitelist_roles:list=None,
    antispam_whitelist_channels:list=None,
    antispam_max_messages:int=None,
    antispam_max_interval:int=None,
    antispam_max_mentions:int=None,
    antispam_max_emojis:int=None,
    antispam_max_caps:int=None,
    antispam_punishment:str=None,
    antispam_punishment_duration:int=None,
    antibadwords_enabled:bool=None,
    antibadwords_rule_id:int=None,
    antibadwords_whitelist_roles:list=None,
    antibadwords_whitelist_channels:list=None,
    antibadwords_words:list=None,
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
    antilink_enabled:bool=None,
    antilink_rule_id:int=None,
    antilink_whitelist_roles:list=None,
    antilink_whitelist_channels:list=None,
    antispam_enabled:bool=None,
    antispam_whitelist_roles:list=None,
    antispam_whitelist_channels:list=None,
    antispam_max_messages:int=None,
    antispam_max_interval:int=None,
    antispam_max_mentions:int=None,
    antispam_max_emojis:int=None,
    antispam_max_caps:int=None,
    antispam_punishment:str=None,
    antispam_punishment_duration:int=None,
    antibadwords_enabled:bool=None,
    antibadwords_rule_id:int=None,
    antibadwords_whitelist_roles:list=None,
    antibadwords_whitelist_channels:list=None,
    antibadwords_words:list=None,
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
                asyncio.create_task(cache_module.automod_cache.delete(guild_id=r['guild_id']))
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

