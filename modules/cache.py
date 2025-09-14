import asyncio
from databases import guilds as guilds_db
from databases import guilds_log as guilds_log_db
from databases import users as users_db
from databases import j2c as j2c_db
from databases import j2c_settings as j2c_settings_db
from databases import antinuke_settings as antinuke_settings_db
from databases import antinuke_bypass as antinuke_bypass_db
from databases import welcomer_settings as welcomer_settings_db
from databases import guilds_backup as guilds_backup_db
from databases import redeem_codes as redeem_codes_db
from databases import afk as afk_db
from databases import snipe_data as snipe_data_db
from databases import ignore_data as ignore_data_db
from databases import ban_data as ban_data_db
from databases import automod as automod_db
from databases import custom_roles as custom_roles_db
from databases import custom_roles_permissions as custom_roles_permissions_db
from databases import media_channels as media_channels_db
from databases import auto_responder as auto_responder_db
from databases import giveaways as giveaways_db
from databases import giveaways_permissions as giveaways_permissions_db
from databases import ticket_settings as ticket_settings_db
from databases import shop as shop_db
from databases import music as music_db

from cache.cache import cache
from services.logging import logger

import json

class Guilds:
    def __init__(self):
        cache.guilds = {}

    async def initialize(self):
        guild_datas = await guilds_db.get_all()
        for data in guild_datas:
            cache.guilds[str(data['guild_id'])] = data
        logger.info(f"All Guilds cache loaded ✅")

    async def delete(self, guild_id):
        if str(guild_id) in cache.guilds:
            del cache.guilds[str(guild_id)]
            logger.info(f"Guild - {guild_id} cache deleted ✅")
        else:
            logger.error(f"Guild - {guild_id} cache not found ❌")

    async def update(self, guild_id, data=None):
        if not data:
            data = await guilds_db.get(guild_id=guild_id)
        if not data:
            logger.error(f"Guild - {guild_id} cache not found ❌")
            return
        cache.guilds[str(guild_id)] = data
        logger.info(f"Guild - {guild_id} cache updated ✅")

class Users:
    def __init__(self):
        cache.users = {}
        cache.owners = []
        cache.admins = []

    async def initialize(self):
        cache.users = {}
        cache.owners = []
        cache.admins = []
        user_datas = await users_db.get_all()
        for data in user_datas:
            cache.users[str(data['user_id'])] = data
            
            if data.get('type') == 'owner':
                cache.owners.append(data['user_id'])
            elif data.get('type') == 'admin':
                cache.admins.append(data['user_id'])
            
        logger.info(f"All Users cache loaded ✅")

    async def delete(self, user_id):
        if str(user_id) in cache.users:
            del cache.users[str(user_id)]
            logger.info(f"User - {user_id} cache deleted ✅")
        else:
            logger.error(f"User - {user_id} cache not found ❌")

    async def update(self, user_id, data=None):
        if not data:
            data = await users_db.get(user_id=user_id)
        if not data:
            logger.error(f"User - {user_id} cache not found ❌")
            return
        cache.users[str(user_id)] = data
        logger.info(f"User - {user_id} cache updated ✅")

class Guilds_log:
    def __init__(self):
        cache.guilds_log = {}

    async def initialize(self):
        cache.guilds_log = {}
        guild_datas = await guilds_log_db.get_all()
        for data in guild_datas:
            cache.guilds_log[str(data['guild_id'])] = data
        logger.info(f"All Guilds log cache loaded ✅")

    async def delete(self, guild_id):
        if str(guild_id) in cache.guilds_log:
            del cache.guilds_log[str(guild_id)]
            logger.info(f"Guild - {guild_id} log cache deleted ✅")
        else:
            logger.error(f"Guild - {guild_id} log cache not found ❌")

    async def update(self, guild_id, data=None):
        if not data:
            data = await guilds_log_db.get(guild_id=guild_id)
        if not data:
            logger.error(f"Guild - {guild_id} log cache not found ❌")
            return
        cache.guilds_log[str(guild_id)] = data
        logger.info(f"Guild - {guild_id} log cache updated ✅")

class J2c:
    def __init__(self):
        cache.j2c = {}

    async def initialize(self):
        cache.j2c = {}
        j2c_datas = await j2c_db.get_all()
        for data in j2c_datas:
            cache.j2c[str(data['channel_id'])] = data
        logger.info(f"All J2C cache loaded ✅")

    async def delete(self, channel_id):
        if str(channel_id) in cache.j2c:
            del cache.j2c[str(channel_id)]
            logger.info(f"J2C - {channel_id} cache deleted ✅")
        else:
            logger.error(f"J2C - {channel_id} cache not found ❌")

    async def update(self, channel_id, data=None):
        if not data:
            data = await j2c_db.get(channel_id=channel_id)
        if not data:
            logger.error(f"J2C - {channel_id} cache not found ❌")
            return
        cache.j2c[str(channel_id)] = data
        logger.info(f"J2C - {channel_id} cache updated ✅")

class j2c_settings:
    def __init__(self):
        cache.j2c_settings = {}

    async def initialize(self):
        cache.j2c_settings = {}
        j2c_settings_datas = await j2c_settings_db.get_all()
        for data in j2c_settings_datas:
            cache.j2c_settings[str(data['guild_id'])] = data
        logger.info(f"All J2C settings cache loaded ✅")

    async def delete(self, guild_id):
        if str(guild_id) in cache.j2c_settings:
            del cache.j2c_settings[str(guild_id)]
            logger.info(f"J2C settings - {guild_id} cache deleted ✅")
        else:
            logger.error(f"J2C settings - {guild_id} cache not found ❌")

    async def update(self, guild_id, data=None):
        if not data:
            data = await j2c_settings_db.get(guild_id=guild_id)
        if not data:
            logger.error(f"J2C settings - {guild_id} cache not found ❌")
            return
        cache.j2c_settings[str(guild_id)] = data
        logger.info(f"J2C settings - {guild_id} cache updated ✅")

class Antinuke_settings:
    def __init__(self):
        cache.antinuke_settings = {}

    async def initialize(self):
        cache.antinuke_settings = {}
        antinuke_settings_datas = await antinuke_settings_db.get_all()
        for data in antinuke_settings_datas:
            cache.antinuke_settings[str(data['guild_id'])] = data
        logger.info(f"All Antinuke settings cache loaded ✅")

    async def delete(self, guild_id):
        if str(guild_id) in cache.antinuke_settings:
            del cache.antinuke_settings[str(guild_id)]
            logger.info(f"Antinuke settings - {guild_id} cache deleted ✅")
        else:
            logger.error(f"Antinuke settings - {guild_id} cache not found ❌")

    async def update(self, guild_id, data=None):
        if not data:
            data = await antinuke_settings_db.get(guild_id=guild_id)
        if not data:
            logger.error(f"Antinuke settings - {guild_id} cache not found ❌")
            return
        cache.antinuke_settings[str(guild_id)] = data
        logger.info(f"Antinuke settings - {guild_id} cache updated ✅")

class antinuke_bypass:
    def __init__(self):
        cache.antinuke_bypass = {}

    async def initialize(self):
        cache.antinuke_bypass = {}
        antinuke_bypass_datas = await antinuke_bypass_db.get_all()
        for data in antinuke_bypass_datas:
            if str(data['guild_id']) not in cache.antinuke_bypass:
                cache.antinuke_bypass[str(data['guild_id'])] = {}
            cache.antinuke_bypass[str(data['guild_id'])][str(data['user_id'])] = data
        logger.info(f"All Antinuke bypass cache loaded ✅")

    async def delete(self, guild_id, user_id):
        if str(guild_id) in cache.antinuke_bypass:
            if str(user_id) in cache.antinuke_bypass[str(guild_id)]:
                del cache.antinuke_bypass[str(guild_id)][str(user_id)]
                logger.info(f"Antinuke bypass - {guild_id} - {user_id} cache deleted ✅")
            else:
                logger.error(f"Antinuke bypass - {guild_id} - {user_id} cache not found ❌")
        else:
            logger.error(f"Antinuke bypass - {guild_id} cache not found ❌")

    async def update(self, guild_id, user_id, data=None):
        if not data:
            data = await antinuke_bypass_db.get(guild_id=guild_id, user_id=user_id)
        if not data:
            logger.error(f"Antinuke bypass - {guild_id} - {user_id} cache not found ❌")
            return
        if str(guild_id) not in cache.antinuke_bypass:
            cache.antinuke_bypass[str(guild_id)] = {}
        cache.antinuke_bypass[str(guild_id)][str(user_id)] = data
        logger.info(f"Antinuke bypass - {guild_id} - {user_id} cache updated ✅")

class Guilds_welcomer:
    def __init__(self):
        cache.welcomer_settings = {}

    async def initialize(self):
        cache.welcomer_settings = {}
        welcomer_settings_datas = await welcomer_settings_db.get_all()
        for data in welcomer_settings_datas:
            cache.welcomer_settings[str(data['guild_id'])] = data
        logger.info(f"All Welcomer settings cache loaded ✅")

    async def delete(self, guild_id):
        if str(guild_id) in cache.welcomer_settings:
            del cache.welcomer_settings[str(guild_id)]
            logger.info(f"Welcomer settings - {guild_id} cache deleted ✅")
        else:
            logger.error(f"Welcomer settings - {guild_id} cache not found ❌")

    async def update(self, guild_id, data=None):
        if not data:
            data = await welcomer_settings_db.get(guild_id=guild_id)
        if not data:
            logger.error(f"Welcomer settings - {guild_id} cache not found ❌")
            return
        cache.welcomer_settings[str(guild_id)] = data
        logger.info(f"Welcomer settings - {guild_id} cache updated ✅")

class Guilds_Backup:
    def __init__(self):
        cache.guilds_backup = {}

    async def initialize(self):
        cache.guilds_backup = {}
        guild_datas = await guilds_backup_db.get_all()
        for data in guild_datas:
            if data['guild_id'] not in cache.guilds_backup:
                cache.guilds_backup[str(data['guild_id'])] = []
            cache.guilds_backup[str(data['guild_id'])].append(data)
        logger.info(f"All Guilds backup cache loaded ✅")

    async def delete(self, guild_id, id):
        if str(guild_id) in cache.guilds_backup:
            for backup in cache.guilds_backup[str(guild_id)]:
                if backup['id'] == id:
                    cache.guilds_backup[str(guild_id)].remove(backup)
                    logger.info(f"Guild - {guild_id} backup - {id} cache deleted ✅")
                    return
            logger.error(f"Guild - {guild_id} backup - {id} cache not found ❌")
        else:
            logger.error(f"Guild - {guild_id} backup cache not found ❌")

    async def update(self, guild_id, data):
        if not data:
            logger.error(f"Guild - {guild_id} backup cache not found ❌")
            return
        if str(guild_id) not in cache.guilds_backup:
            cache.guilds_backup[str(guild_id)] = []
        else:
            for backup in cache.guilds_backup[str(guild_id)]:
                if backup['id'] == data['id']:
                    cache.guilds_backup[str(guild_id)].remove(backup)
                    break
        cache.guilds_backup[str(guild_id)].append(data)
        logger.info(f"Guild - {guild_id} backup cache updated ✅")

class Redeem_codes:
    def __init__(self):
        cache.redeem_codes = {}

    async def initialize(self):
        cache.redeem_codes = {}
        redeem_datas = await redeem_codes_db.get_all()
        for data in redeem_datas:
            cache.redeem_codes[str(data['code'])] = data
        logger.info(f"All Redeem codes cache loaded ✅")

    async def delete(self, code):
        if str(code) in cache.redeem_codes:
            del cache.redeem_codes[str(code)]
            logger.info(f"Redeem code - {code} cache deleted ✅")
        else:
            logger.error(f"Redeem code - {code} cache not found ❌")

    async def update(self, code, data=None):
        if not data:
            data = await redeem_codes_db.get(code=code)
        if not data:
            logger.error(f"Redeem code - {code} cache not found ❌")
            return
        cache.redeem_codes[str(code)] = data
        logger.info(f"Redeem code - {code} cache updated ✅")

class Afk:
    def __init__(self):
        cache.afk = {
            "guilds": {},
            "global": {}
        }

    async def initialize(self):
        cache.afk = {
            "guilds": {},
            "global": {}
        }
        afk_datas = await afk_db.get_all()
        for data in afk_datas:
            if data['guild_id']:
                if data['guild_id'] not in cache.afk['guilds']:
                    cache.afk['guilds'][str(data['guild_id'])] = {}
                cache.afk['guilds'][str(data['guild_id'])][str(data['user_id'])] = data
            else:
                cache.afk['global'][str(data['user_id'])] = data
        logger.info(f"All AFK cache loaded ✅")

    async def delete(self, guild_id, user_id):
        if guild_id:
            if str(guild_id) in cache.afk.get('guilds', {}):
                if str(user_id) in cache.afk['guilds'][str(guild_id)]:
                    del cache.afk['guilds'][str(guild_id)][str(user_id)]
                    logger.info(f"AFK - {guild_id} - {user_id} cache deleted ✅")
                else:
                    logger.error(f"AFK - {guild_id} - {user_id} cache not found ❌")
            else:
                logger.error(f"AFK - {guild_id} cache not found ❌")
        else:
            if str(user_id) in cache.afk.get('global', {}):
                del cache.afk['global'][str(user_id)]
                logger.info(f"AFK - {user_id} cache deleted ✅")
            else:
                logger.error(f"AFK - {user_id} cache not found ❌")

    async def update(self, guild_id, user_id, data=None):
        if not data:
            data = await afk_db.get(guild_id=guild_id, user_id=user_id)
        if not data:
            logger.error(f"AFK - {guild_id} - {user_id} cache not found ❌")
            return
        if guild_id:
            if str(guild_id) not in cache.afk['guilds']:
                cache.afk['guilds'][str(guild_id)] = {}
            cache.afk['guilds'][str(guild_id)][str(user_id)] = data
            logger.info(f"Afk - {guild_id} - {user_id} cache updated ✅")
        else:
            cache.afk['global'][str(user_id)] = data
            logger.info(f"Afk - {user_id} cache updated ✅")

class SnipeData:
    def __init__(self):
        cache.snipe_data = {}
    
    async def initialize(self):
        cache.snipe_data = {}
        snipe_datas = await snipe_data_db.get_all()
        for data in snipe_datas:
            if data.get('type') == 'delete':
                if 'delete' not in cache.snipe_data:
                    cache.snipe_data['delete'] = {}
                cache.snipe_data['delete'][str(data['channel_id'])] = data
            elif data.get('type') == 'edit':
                if 'edit' not in cache.snipe_data:
                    cache.snipe_data['edit'] = {}
                cache.snipe_data['edit'][str(data['channel_id'])] = data
            else:
                logger.warning(f"Unknown snipe data type {data.get('type')}")
        logger.info(f"All Snipe data cache loaded ✅")

    async def delete(self, channel_id, type):
        if type == 'delete':
            if 'delete' in cache.snipe_data:
                if str(channel_id) in cache.snipe_data['delete']:
                    del cache.snipe_data['delete'][str(channel_id)]
                    logger.info(f"Snipe delete - {channel_id} cache deleted ✅")
                else:
                    logger.error(f"Snipe delete - {channel_id} cache not found ❌")
            else:
                logger.error(f"Snipe delete cache not found ❌")
        elif type == 'edit':
            if 'edit' in cache.snipe_data:
                if str(channel_id) in cache.snipe_data['edit']:
                    del cache.snipe_data['edit'][str(channel_id)]
                    logger.info(f"Snipe edit - {channel_id} cache deleted ✅")
                else:
                    logger.error(f"Snipe edit - {channel_id} cache not found ❌")
            else:
                logger.error(f"Snipe edit cache not found ❌")
        else:
            logger.error(f"Unknown snipe data type {type}")
    
    async def update(self, channel_id, type=None, data=None):
        if not data:
            data = await snipe_data_db.get(channel_id=channel_id, type=type)
        if not type:
            type = data.get('type')
        if not data:
            logger.error(f"Snipe - {channel_id} - {type} cache not found ❌")
            return
        if type == 'delete':
            if 'delete' not in cache.snipe_data:
                cache.snipe_data['delete'] = {}
            cache.snipe_data['delete'][str(channel_id)] = data
            logger.info(f"Snipe delete - {channel_id} cache updated ✅")
        elif type == 'edit':
            if 'edit' not in cache.snipe_data:
                cache.snipe_data['edit'] = {}
            cache.snipe_data['edit'][str(channel_id)] = data
            logger.info(f"Snipe edit - {channel_id} cache updated ✅")
        else:
            logger.error(f"Unknown snipe data type {type}")

class IgnoreData:
    def __init__(self):
        cache.ignore_data = {
            "users": {},
            "channels": {}
        }
        logger.info(f"All Ignore data cache initialized ✅")

    async def initialize(self):
        cache.ignore_data = {
            "users": {},
            "channels": {}
        }
        ignore_datas = await ignore_data_db.get_all()
        for data in ignore_datas:
            if data.get('type') == 'user':
                if str(data.get('guild_id')) not in cache.ignore_data['users']:
                    cache.ignore_data['users'][str(data.get('guild_id'))] = {}
                cache.ignore_data['users'][str(data.get('guild_id'))][str(data['user_id'])] = data
            elif data.get('type') == 'channel':
                if str(data.get('guild_id')) not in cache.ignore_data['channels']:
                    cache.ignore_data['channels'][str(data.get('guild_id'))] = {}
                cache.ignore_data['channels'][str(data.get('guild_id'))][str(data['channel_id'])] = data
            else:
                logger.warning(f"Unknown ignore data type {data.get('type')}")
        logger.info(f"All Ignore data cache loaded ✅")

    async def delete(self, guild_id, user_id=None, channel_id=None):
        if user_id:
            if str(user_id) in cache.ignore_data['users'].get(str(guild_id), {}):
                del cache.ignore_data['users'][str(guild_id)][str(user_id)]
                logger.info(f"Ignore user - {user_id} cache deleted ✅")
            else:
                logger.error(f"Ignore user - {user_id} cache not found ❌")
        elif channel_id:
            if str(channel_id) in cache.ignore_data['channels'].get(str(guild_id), {}):
                del cache.ignore_data['channels'][str(guild_id)][str(channel_id)]
                logger.info(f"Ignore channel - {channel_id} cache deleted ✅")
            else:
                logger.error(f"Ignore channel - {channel_id} cache not found ❌")
        else:
            logger.error(f"Unknown ignore data type")
    
    async def update(self, guild_id, user_id=None, channel_id=None, data=None):
        if not data:
            data = await ignore_data_db.get(guild_id=guild_id, user_id=user_id, channel_id=channel_id)
        if not data:
            logger.error(f"Ignore - {guild_id} - {user_id} - {channel_id} cache not found ❌")
            return
        if user_id:
            if str(guild_id) not in cache.ignore_data['users']:
                cache.ignore_data['users'][str(guild_id)] = {}
            cache.ignore_data['users'][str(guild_id)][str(user_id)] = data
            logger.info(f"Ignore user - {user_id} cache updated ✅")
        elif channel_id:
            if str(guild_id) not in cache.ignore_data['channels']:
                cache.ignore_data['channels'][str(guild_id)] = {}
            cache.ignore_data['channels'][str(guild_id)][str(channel_id)] = data
            logger.info(f"Ignore channel - {channel_id} cache updated ✅")
        else:
            logger.error(f"Unknown ignore data type")
            
class BanData:
    def __init__(self):
        cache.ban_data = {
            "guilds": {},
            "users": {}
        }
        logger.info(f"All Ban data cache initialized ✅")

    async def initialize(self):
        cache.ban_data = {
            "guilds": {},
            "users": {}
        }
        ban_datas = await ban_data_db.get_all()
        for data in ban_datas:
            if data.get('guild_id'):
                cache.ban_data['guilds'][str(data.get('guild_id'))] = data
            elif data.get('user_id'):
                cache.ban_data['users'][str(data.get('user_id'))] = data
            else:
                logger.warning(f"Unknown ban data type {data.get('type')}")

    async def delete(self, guild_id=None, user_id=None):
        if user_id:
            if str(user_id) in cache.ban_data['users']:
                del cache.ban_data['users'][str(user_id)]
                logger.info(f"Ban user - {user_id} cache deleted ✅")
            else:
                logger.error(f"Ban user - {user_id} cache not found ❌")
        elif guild_id:
            if str(guild_id) in cache.ban_data['guilds']:
                del cache.ban_data['guilds'][str(guild_id)]
                logger.info(f"Ban guild - {guild_id} cache deleted ✅")
            else:
                logger.error(f"Ban guild - {guild_id} cache not found ❌")

    async def update(self, guild_id=None, user_id=None, data=None):
        if not data:
            data = await ban_data_db.get(guild_id=guild_id, user_id=user_id)
        if not data:
            logger.error(f"Ban - {guild_id} - {user_id} cache not found ❌")
            return
        if user_id:
            cache.ban_data['users'][str(user_id)] = data
            logger.info(f"Ban user - {user_id} cache updated ✅")
        elif guild_id:
            cache.ban_data['guilds'][str(guild_id)] = data
            logger.info(f"Ban guild - {guild_id} cache updated ✅")

class Automod:
    def __init__(self):
        cache.automod = {}
        logger.info(f"All Automod cache initialized ✅")
    
    async def initialize(self):
        cache.automod = {}
        automod_datas = await automod_db.get_all()
        for data in automod_datas:
            cache.automod[str(data['guild_id'])] = data
        logger.info(f"All Automod cache loaded ✅")

    async def delete(self, guild_id):
        if str(guild_id) in cache.automod:
            del cache.automod[str(guild_id)]
            logger.info(f"Automod - {guild_id} cache deleted ✅")
        else:
            logger.error(f"Automod - {guild_id} cache not found ❌")

    async def update(self, guild_id, data=None):
        if not data:
            data = await automod_db.get(guild_id=guild_id)
        if not data:
            logger.error(f"Automod - {guild_id} cache not found ❌")
            return
        cache.automod[str(guild_id)] = data
        logger.info(f"Automod - {guild_id} cache updated ✅")


class CustomRoles:
    def __init__(self):
        cache.custom_roles = {}
        logger.info(f"All Custom roles cache initialized ✅")

    async def initialize(self):
        cache.custom_roles = {}
        custom_role_datas = await custom_roles_db.get_all()
        for data in custom_role_datas:
            if data.get('guild_id'):
                if str(data['guild_id']) not in cache.custom_roles:
                    cache.custom_roles[str(data['guild_id'])] = {}
                cache.custom_roles[str(data['guild_id'])][str(data['name'])] = data
            else:
                logger.warning(f"Unknown custom role id {data.get('id')}")
        logger.info(f"All Custom roles cache loaded ✅")

    async def delete(self, guild_id, name):
        if str(guild_id) in cache.custom_roles:
            if str(name) in cache.custom_roles[str(guild_id)]:
                del cache.custom_roles[str(guild_id)][str(name)]
                logger.info(f"Custom role - {guild_id} - {name} cache deleted ✅")
            else:
                logger.error(f"Custom role - {guild_id} - {name} cache not found ❌")
        else:
            logger.error(f"Custom role - {guild_id} cache not found ❌")

    async def update(self, guild_id, name, data=None):
        if not data:
            data = await custom_roles_db.get(guild_id=guild_id, name=name)
        if not data:
            logger.error(f"Custom role - {guild_id} - {name} cache not found ❌")
            return
        if str(guild_id) not in cache.custom_roles:
            cache.custom_roles[str(guild_id)] = {}
        cache.custom_roles[str(guild_id)][str(name)] = data
        logger.info(f"Custom role - {guild_id} - {name} cache updated ✅")


class CustomRolesPermissions:
    def __init__(self):
        cache.custom_roles_permissions = {}
        logger.info(f"All Custom roles permissions cache initialized ✅")

    async def initialize(self):
        cache.custom_roles_permissions = {}
        custom_role_permission_datas = await custom_roles_permissions_db.get_all()
        for data in custom_role_permission_datas:
            if data.get('guild_id'):
                cache.custom_roles_permissions[str(data['guild_id'])] = data
            else:
                logger.warning(f"Unknown custom role permission id {data.get('id')}")
        logger.info(f"All Custom roles permissions cache loaded ✅")

    async def delete(self, guild_id):
        if str(guild_id) in cache.custom_roles_permissions:
            del cache.custom_roles_permissions[str(guild_id)]
            logger.info(f"Custom role permission - {guild_id} cache deleted ✅")
        else:
            logger.error(f"Custom role permission - {guild_id} cache not found ❌")

    async def update(self, guild_id, data=None):
        if not data:
            data = await custom_roles_permissions_db.get(guild_id=guild_id)
        if not data:
            logger.error(f"Custom role permission - {guild_id} cache not found ❌")
            return
        cache.custom_roles_permissions[str(guild_id)] = data
        logger.info(f"Custom role permission - {guild_id} cache updated ✅")


class MediaChannels:
    def __init__(self):
        cache.media_channels = {}
        logger.info(f"All Media channels cache initialized ✅")

    async def initialize(self):
        cache.media_channels = {}
        media_channel_datas = await media_channels_db.get_all()
        for data in media_channel_datas:
            if data.get('guild_id'):
                if str(data['guild_id']) not in cache.media_channels:
                    cache.media_channels[str(data['guild_id'])] = {}
                cache.media_channels[str(data['guild_id'])][str(data['channel_id'])] = data
            else:
                logger.warning(f"Unknown media channel id {data.get('id')}")
        logger.info(f"All Media channels cache loaded ✅")

    async def delete(self, guild_id, channel_id):
        if str(guild_id) in cache.media_channels:
            if str(channel_id) in cache.media_channels[str(guild_id)]:
                del cache.media_channels[str(guild_id)][str(channel_id)]
                logger.info(f"Media channel - {guild_id} - {channel_id} cache deleted ✅")
            else:
                logger.error(f"Media channel - {guild_id} - {channel_id} cache not found ❌")
        else:
            logger.error(f"Media channel - {guild_id} cache not found ❌")

    async def update(self, guild_id, channel_id, data=None):
        if not data:
            data = await media_channels_db.get(guild_id=guild_id, channel_id=channel_id)
        if not data:
            logger.error(f"Media channel - {guild_id} - {channel_id} cache not found ❌")
            return
        if str(guild_id) not in cache.media_channels:
            cache.media_channels[str(guild_id)] = {}
        cache.media_channels[str(guild_id)][str(channel_id)] = data
        logger.info(f"Media channel - {guild_id} - {channel_id} cache updated ✅")


class AutoResponder:
    def __init__(self):
        cache.auto_responder = {}
        logger.info(f"All Auto responder cache initialized ✅")

    async def initialize(self):
        cache.auto_responder = {}
        auto_responder_datas = await auto_responder_db.get_all()
        for data in auto_responder_datas:
            if data.get('guild_id'):
                if str(data['guild_id']) not in cache.auto_responder:
                    cache.auto_responder[str(data['guild_id'])] = {}
                cache.auto_responder[str(data['guild_id'])][str(data['keyword'])] = data
            else:
                logger.warning(f"Unknown auto responder id {data.get('id')}")
        logger.info(f"All Auto responder cache loaded ✅")

    async def delete(self, guild_id, keyword):
        if str(guild_id) in cache.auto_responder:
            if str(keyword) in cache.auto_responder[str(guild_id)]:
                del cache.auto_responder[str(guild_id)][str(keyword)]
                logger.info(f"Auto responder - {guild_id} - {keyword} cache deleted ✅")
            else:
                logger.error(f"Auto responder - {guild_id} - {keyword} cache not found ❌")
        else:
            logger.error(f"Auto responder - {guild_id} cache not found ❌")

    async def update(self, guild_id, keyword, data=None):
        if not data:
            data = await auto_responder_db.get(guild_id=guild_id, keyword=keyword)
        if not data:
            logger.error(f"Auto responder - {guild_id} - {keyword} cache not found ❌")
            return
        if str(guild_id) not in cache.auto_responder:
            cache.auto_responder[str(guild_id)] = {}
        cache.auto_responder[str(guild_id)][str(keyword)] = data
        logger.info(f"Auto responder - {guild_id} - {keyword} cache updated ✅")


class Giveaways:
    def __init__(self):
        cache.giveaways = {}
        logger.info(f"All Giveaways cache initialized ✅")

    async def initialize(self):
        cache.giveaways = {}
        giveaway_datas = await giveaways_db.get_all()
        for data in giveaway_datas:
            if data.get('guild_id'):
                if data.get('ended'):
                    continue
                if str(data['guild_id']) not in cache.giveaways:
                    cache.giveaways[str(data['guild_id'])] = {}
                cache.giveaways[str(data['guild_id'])][str(data['giveaway_id'])] = data
            else:
                logger.warning(f"Unknown giveaway id {data.get('id')}")
        logger.info(f"All Giveaways cache loaded ✅")

    async def delete(self, guild_id, giveaway_id):
        if str(guild_id) in cache.giveaways:
            if str(giveaway_id) in cache.giveaways[str(guild_id)]:
                del cache.giveaways[str(guild_id)][str(giveaway_id)]
                logger.info(f"Giveaway - {guild_id} - {giveaway_id} cache deleted ✅")
            else:
                logger.error(f"Giveaway - {guild_id} - {giveaway_id} cache not found ❌")
        else:
            logger.error(f"Giveaway - {guild_id} cache not found ❌")

    async def update(self, guild_id, giveaway_id, data=None):
        if not data:
            data = await giveaways_db.get(guild_id=guild_id, giveaway_id=giveaway_id)
        if not data:
            logger.error(f"Giveaway - {guild_id} - {giveaway_id} cache not found ❌")
            return
        if data.get('ended'):
            await self.delete(guild_id, giveaway_id)
            return logger.error(f"Giveaway - {guild_id} - {giveaway_id} already ended")
        if str(guild_id) not in cache.giveaways:
            cache.giveaways[str(guild_id)] = {}
        cache.giveaways[str(guild_id)][str(giveaway_id)] = data
        logger.info(f"Giveaway - {guild_id} - {giveaway_id} cache updated ✅")

class GiveawaysPermissions:
    def __init__(self):
        cache.giveaways_permissions = {}
        logger.info(f"All Giveaways permissions cache initialized ✅")

    async def initialize(self):
        cache.giveaways_permissions = {}
        giveaway_permission_datas = await giveaways_permissions_db.get_all()
        for data in giveaway_permission_datas:
            if data.get('guild_id'):
                cache.giveaways_permissions[str(data['guild_id'])] = data
            else:
                logger.warning(f"Unknown giveaway permission id {data.get('id')}")
        logger.info(f"All Giveaways permissions cache loaded ✅")

    async def delete(self, guild_id):
        if str(guild_id) in cache.giveaways_permissions:
            del cache.giveaways_permissions[str(guild_id)]
            logger.info(f"Giveaway permission - {guild_id} cache deleted ✅")
        else:
            logger.error(f"Giveaway permission - {guild_id} cache not found ❌")

    async def update(self, guild_id, data=None):
        if not data:
            data = await giveaways_permissions_db.get(guild_id=guild_id)
        if not data:
            logger.error(f"Giveaway permission - {guild_id} cache not found ❌")
            return
        cache.giveaways_permissions[str(guild_id)] = data
        logger.info(f"Giveaway permission - {guild_id} cache updated ✅")

class TicketSettings:
    def __init__(self):
        cache.ticket_settings = {}
        logger.info(f"All Ticket settings cache initialized ✅")

    async def initialize(self):
        cache.ticket_settings = {}
        ticket_settings_datas = await ticket_settings_db.get_all()
        for data in ticket_settings_datas:
            if data.get('guild_id'):
                if str(data['guild_id']) not in cache.ticket_settings:
                    cache.ticket_settings[str(data['guild_id'])] = {}
                cache.ticket_settings[str(data['guild_id'])][str(data['ticket_module_id'])] = data
            else:
                logger.warning(f"Unknown ticket settings id {data.get('id')}")
        logger.info(f"All Ticket settings cache loaded ✅")

    async def delete(self, guild_id, ticket_module_id):
        if str(guild_id) in cache.ticket_settings:
            if str(ticket_module_id) in cache.ticket_settings[str(guild_id)]:
                del cache.ticket_settings[str(guild_id)][str(ticket_module_id)]
                logger.info(f"Ticket settings - {guild_id} - {ticket_module_id} cache deleted ✅")
            else:
                logger.error(f"Ticket settings - {guild_id} - {ticket_module_id} cache not found ❌")
        else:
            logger.error(f"Ticket settings - {guild_id} cache not found ❌")

    async def update(self, guild_id, ticket_module_id, data=None):
        if not data:
            data = await ticket_settings_db.get(guild_id=guild_id, ticket_module_id=ticket_module_id)
        if not data:
            logger.error(f"Ticket settings - {guild_id} - {ticket_module_id} cache not found ❌")
            return
        if str(guild_id) not in cache.ticket_settings:
            cache.ticket_settings[str(guild_id)] = {}
        cache.ticket_settings[str(guild_id)][str(ticket_module_id)] = data
        logger.info(f"Ticket settings - {guild_id} - {ticket_module_id} cache updated ✅")

class Shop:
    def __init__(self):
        cache.shop = {}
        logger.info(f"All Shop cache initialized ✅")

    async def initialize(self):
        cache.shop = {}
        shop_datas = await shop_db.get_all()
        for data in shop_datas:
            cache.shop[str(data['id'])] = data
        logger.info(f"All Shop cache loaded ✅")

    async def delete(self, id: int):
        if str(id) in cache.shop:
            del cache.shop[str(id)]
            logger.info(f"Shop - {id} cache deleted ✅")
        else:
            logger.error(f"Shop - {id} cache not found ❌")

    async def update(self, id, data=None):
        if not data:
            data = await shop_db.get(id=id)
        if not data:
            logger.error(f"Shop - {id} cache not found ❌")
            return
        cache.shop[str(id)] = data
        logger.info(f"Shop - {id} cache updated ✅")

class Music:
    def __init__(self):
        cache.music = {}
        logger.info(f"All Music cache initialized ✅")

    async def initialize(self):
        cache.music = {}
        music_datas = await music_db.get_all()
        for data in music_datas:
            if data.get('guild_id'):
                cache.music[str(data['guild_id'])] = data
            else:
                logger.warning(f"Unknown music id {data.get('id')}")
        logger.info(f"All Music cache loaded ✅")

    async def delete(self, guild_id):
        if str(guild_id) in cache.music:
            del cache.music[str(guild_id)]
            logger.info(f"Music - {guild_id} cache deleted ✅")
        else:
            logger.error(f"Music - {guild_id} cache not found ❌")

    async def update(self, guild_id, data=None):
        if not data:
            data = await music_db.get(guild_id=guild_id)
        if not data:
            logger.error(f"Music - {guild_id} cache not found ❌")
            return
        cache.music[str(guild_id)] = data
        logger.info(f"Music - {guild_id} cache updated ✅")

guilds_cache = Guilds()
users_cache = Users()
guilds_log_cache = Guilds_log()
j2c_cache = J2c()
j2c_settings_cache = j2c_settings()
antinuke_settings_cache = Antinuke_settings()
antinuke_bypass_cache = antinuke_bypass()
guilds_welcomer_cache = Guilds_welcomer()
guilds_backup_cache = Guilds_Backup()
redeem_codes_cache = Redeem_codes()
afk_cache = Afk()
snipe_data_cache = SnipeData()
ignore_data_cache = IgnoreData()
ban_data_cache = BanData()
automod_cache = Automod()
custom_roles_cache = CustomRoles()
custom_roles_permissions_cache = CustomRolesPermissions()
media_channels_cache = MediaChannels()
auto_responder_cache = AutoResponder()
giveaways_cache = Giveaways()
giveaways_permissions_cache = GiveawaysPermissions()
ticket_settings_cache = TicketSettings()
shop_cache = Shop()
music_cache = Music()

async def load_cache():
    await guilds_cache.initialize()
    await users_cache.initialize()
    await guilds_log_cache.initialize()
    await j2c_cache.initialize()
    await j2c_settings_cache.initialize()
    await antinuke_settings_cache.initialize()
    await antinuke_bypass_cache.initialize()
    await guilds_backup_cache.initialize()
    await guilds_welcomer_cache.initialize()
    await redeem_codes_cache.initialize()
    await afk_cache.initialize()
    await snipe_data_cache.initialize()
    await ignore_data_cache.initialize()
    await ban_data_cache.initialize()
    await automod_cache.initialize()
    await custom_roles_cache.initialize()
    await custom_roles_permissions_cache.initialize()
    await media_channels_cache.initialize()
    await auto_responder_cache.initialize()
    await giveaways_cache.initialize()
    await giveaways_permissions_cache.initialize()
    await ticket_settings_cache.initialize()
    await shop_cache.initialize()
    await music_cache.initialize()

    logger.info("All cache loaded ✅")