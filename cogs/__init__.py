from services.logging import logger
from core.Bot import AutoShardedBot
import asyncio

# Import all commands cogs
from .commands.utils import Utils
from .commands.root import Root
from .commands.help import Help
from .commands.fun import Fun
from .commands.moderation import Moderation
from .commands.security import Security
from .commands.music import Music
from .commands.welcomer import Welcomer
from .commands.automod import Automod
from .commands.more import More
from .commands.voice import Voice
from .commands.giveaway import Giveaway
from .commands.ticket import Ticket
from .commands.economy import Economy
import importlib


# Import all events cogs
from .events.on_command import on_command
from .events.ready import ready
from .events.on_member_join import on_member_join
from .events.on_command_error import on_command_error
from .events.on_member_remove import on_member_remove
from .events.on_member_unban import on_member_unban
from .events.message import message
from .events.on_member_update import on_member_update
from .events.on_message_delete import on_message_delete
from .events.on_message_edit import on_message_edit
from .events.on_guild_channel_create import on_guild_channel_create
from .events.on_guild_channel_delete import on_guild_channel_delete
from .events.on_guild_channel_update import on_guild_channel_update
from .events.on_guild_role_create import on_guild_role_create
from .events.on_guild_role_delete import on_guild_role_delete
from .events.on_guild_role_update import on_guild_role_update
from .events.on_guild_emojis_update import on_guild_emojis_update
from .events.on_voice_state_update import on_voice_state_update
from .events.on_webhooks_update import on_webhooks_update
from .events.on_invite_create import on_invite_create
from .events.on_invite_delete import on_invite_delete
from .events.on_guild_update import on_guild_update
from .events.on_guild_join import on_guild_join
from .events.on_guild_remove import on_guild_remove
from .events.wavelink import Wavelink



from modules.startup import check_guilds_subscription,check_users_subscription,resume_afk_functions

from connections import lavalink


from cogs.startup import tickets_creator

async def setup(bot: AutoShardedBot):


    await bot.add_cog(Utils(bot=bot))
    logger.info("Loaded utils")


    await bot.add_cog(Security(bot=bot))
    logger.info("Loaded Security")
    await bot.add_cog(Automod(bot=bot))
    logger.info("Loaded Automod")
    await bot.add_cog(Moderation(bot=bot))
    logger.info("Loaded Moderation")
    await bot.add_cog(Ticket(bot=bot))
    logger.info("Loaded Ticket")
    await bot.add_cog(Welcomer(bot=bot))
    logger.info("Loaded Welcomer")
    await bot.add_cog(Music(bot=bot))
    logger.info("Loaded Music")

    await bot.add_cog(Giveaway(bot=bot))
    logger.info("Loaded Giveaways")
    await bot.add_cog(Help(bot=bot))
    logger.info("Loaded help")
    await bot.add_cog(Fun(bot=bot))
    logger.info("Loaded fun")
    await bot.add_cog(Voice(bot=bot))
    logger.info("Loaded Voice")
    await bot.add_cog(Economy(bot=bot))
    logger.info("Loaded Economy")
    await bot.add_cog(More(bot=bot))
    logger.info("Loaded More")




    await bot.add_cog(Root(bot=bot))
    logger.info("Loaded root")


    await bot.add_cog(on_command(bot=bot))
    logger.info("Loaded on_command")
    await bot.add_cog(Wavelink(bot=bot))
    logger.info("Loaded wavelink")
    await bot.add_cog(message(bot=bot))
    logger.info("Loaded message")
    await bot.add_cog(on_guild_join(bot=bot))
    logger.info("Loaded on_guild_join")
    await bot.add_cog(on_guild_remove(bot=bot))
    logger.info("Loaded on_guild_remove")
    await bot.add_cog(on_member_join(bot=bot))
    logger.info("Loaded on_member_join")
    await bot.add_cog(on_member_remove(bot=bot))
    logger.info("Loaded on_member_remove")
    await bot.add_cog(ready(bot=bot))
    logger.info("Loaded ready")
    await bot.add_cog(on_command_error(bot=bot))
    logger.info("Loaded on_command_error")
    await bot.add_cog(on_member_unban(bot=bot))
    logger.info("Loaded on_member_unban")
    await bot.add_cog(on_member_update(bot=bot))
    logger.info("Loaded on_member_update")
    await bot.add_cog(on_message_delete(bot=bot))
    logger.info("Loaded on_message_delete")
    await bot.add_cog(on_message_edit(bot=bot))
    logger.info("Loaded on_message_edit")
    await bot.add_cog(on_guild_channel_create(bot=bot))
    logger.info("Loaded on_guild_channel_create")
    await bot.add_cog(on_guild_channel_delete(bot=bot))
    logger.info("Loaded on_guild_channel_delete")
    await bot.add_cog(on_guild_channel_update(bot=bot))
    logger.info("Loaded on_guild_channel_update")
    await bot.add_cog(on_guild_role_create(bot=bot))
    logger.info("Loaded on_guild_role_create")
    await bot.add_cog(on_guild_role_delete(bot=bot))
    logger.info("Loaded on_guild_role_delete")
    await bot.add_cog(on_guild_role_update(bot=bot))
    logger.info("Loaded on_guild_role_update")
    await bot.add_cog(on_guild_emojis_update(bot=bot))
    logger.info("Loaded on_guild_emojis_update")
    await bot.add_cog(on_voice_state_update(bot=bot))
    logger.info("Loaded on_voice_state_update")
    await bot.add_cog(on_webhooks_update(bot=bot))
    logger.info("Loaded on_webhooks_update")
    await bot.add_cog(on_invite_create(bot=bot))
    logger.info("Loaded on_invite_create")
    await bot.add_cog(on_invite_delete(bot=bot))
    logger.info("Loaded on_invite_delete")
    await bot.add_cog(on_guild_update(bot=bot))
    logger.info("Loaded on_guild_update")

    try:
        importlib.reload(lavalink)
        asyncio.create_task(lavalink.on_node(bot))
    except Exception as e:
        pass

    try:
        asyncio.create_task(check_guilds_subscription(bot))
    except Exception as e:
        pass
    try:
        asyncio.create_task(check_users_subscription(bot))
    except Exception as e:
        pass
    try:
        asyncio.create_task(resume_afk_functions(bot))
    except Exception as e:
        pass
    try:
        asyncio.create_task(tickets_creator.resume_ticket_creator(bot))
    except:
        pass
    logger.info("Resumed Ticket Creator")
    try:
        asyncio.create_task(tickets_creator.resume_ticket_closer(bot))
    except:
        pass
    logger.info("Resumed Ticket Closer")
    logger.info("Loaded all cogs")