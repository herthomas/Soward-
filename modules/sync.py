import databases.giveaways_permissions
import databases.guilds
import databases.guilds_log
import databases.users
import databases.j2c
import databases.j2c_settings
import databases.antinuke_settings
import databases.antinuke_bypass
import databases.welcomer_settings
import databases.guilds_backup
import databases.redeem_codes
import databases.afk
import databases.snipe_data
import databases.ignore_data
import databases.ban_data
import databases.automod
import databases.custom_roles
import databases.custom_roles_permissions
import databases.media_channels
import databases.auto_responder
import databases.giveaways
import databases.giveaway_participants
import databases.giveaways_permissions
import databases.ticket_settings
import databases.tickets
import databases.shop
import databases.music

from services.logging import logger

async def loadDataBase():
    await databases.guilds.create_table()
    await databases.guilds_log.create_table()
    await databases.users.create_table()
    await databases.j2c.create_table()
    await databases.j2c_settings.create_table()
    await databases.antinuke_settings.create_table()
    await databases.antinuke_bypass.create_table()
    await databases.welcomer_settings.create_table()
    await databases.guilds_backup.create_table()
    await databases.redeem_codes.create_table()
    await databases.afk.create_table()
    await databases.snipe_data.create_table()
    await databases.ignore_data.create_table()
    await databases.ban_data.create_table()
    await databases.automod.create_table()
    await databases.custom_roles.create_table()
    await databases.custom_roles_permissions.create_table()
    await databases.media_channels.create_table()
    await databases.auto_responder.create_table()
    await databases.giveaways.create_table()
    await databases.giveaway_participants.create_table()
    await databases.giveaways_permissions.create_table()
    await databases.ticket_settings.create_table()
    await databases.tickets.create_table()
    await databases.shop.create_table()
    await databases.music.create_table()
    
    logger.info("Database Loaded ✅")