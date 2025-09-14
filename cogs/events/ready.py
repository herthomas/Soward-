from discord.ext import commands
import wavelink
import traceback, sys

from services.logging import logger
from settings.config import users as users_config

from core.Bot import AutoShardedBot
import asyncio
import requests
from themes import color

import discord

from cogs.startup import giveaways
from cogs.startup import j2c_controller
class ready(commands.Cog):
    def __init__(self, bot):
        self.bot:AutoShardedBot = bot


        
    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        try:
            logger.info(f"Connect as {self.bot.user}")
            try:
                asyncio.create_task(self.activity())
            except:
                pass
            try:
                asyncio.create_task(self.on_ready_startups())
            except:
                pass
            await self.bot.tree.sync()
            logger.info(f"Tree Synced")
            self.bot.developer = await self.bot.fetch_user(users_config.developer)
            if not self.bot.developer:
                self.bot.developer = self.bot.user
            logger.info(f"Developer User Loaded: {self.bot.developer}")
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    async def on_ready_startups(self):
        try:
            asyncio.create_task(giveaways.resume_active_giveaway(self.bot))
        except:
            pass
        logger.info("Resumed Giveaway Controller")
        try:
            asyncio.create_task(j2c_controller.resume_j2c_controllers(self.bot))
        except:
            pass
        logger.info("Resumed J2C Controller")

        

    async def activity(self):
        while not self.bot.is_ready():
            await asyncio.sleep(1)
        while True:
            try:
                activitys = [
                    discord.Activity(type=discord.ActivityType.listening, name=f"/help"),
                    discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.bot.guilds)} servers"),
                    discord.Activity(type=discord.ActivityType.watching, name=f"{sum([guild.member_count for guild in self.bot.guilds if guild.member_count])} users"),
                    discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.bot.commands)} commands"),
                    discord.Activity(type=discord.ActivityType.watching, name=f"{self.bot.urls.WEBSITE}"),
                ]
                for activity in activitys:
                    await self.bot.change_presence(activity=activity)
                    logger.info(f"Changed activity to {activity.type} {activity.name}")
                    await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")



    async def send_shard_log(self, msg, embed_color=color.green):
        try:
            shards_log_webhook = self.bot.channels.shards_log_webhook
            if shards_log_webhook:
                embed = discord.Embed(description=f"{self.bot.emoji.SUCCESS if embed_color == color.green else self.bot.emoji.ERROR} | {msg}", color=embed_color)
                requests.post(shards_log_webhook, json={"embeds": [embed.to_dict()]},timeout=5)
            else:
                logger.warning(f"Could not send shard log: {msg}")
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.Cog.listener()
    async def on_disconnect(self):
        await self.send_shard_log("Disconnected from Discord", embed_color=color.red)
        logger.warning("Disconnected from Discord")

    @commands.Cog.listener()
    async def on_resumed(self):
        await self.send_shard_log("Reconnected to Discord", embed_color=color.orange)
        logger.info("Reconnected to Discord")

    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id):
        await self.send_shard_log(f"Shard {shard_id} is ready", embed_color=color.green)
        logger.info(f"Shard {shard_id} is ready")

    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id):
        await self.send_shard_log(f"Shard {shard_id} is disconnected", embed_color=color.red)
        logger.warning(f"Shard {shard_id} is disconnected")

    @commands.Cog.listener()
    async def on_shard_resumed(self, shard_id):
        await self.send_shard_log(f"Shard {shard_id} is resumed", embed_color=color.orange)
        logger.info(f"Shard {shard_id} is resumed")
    
    # event when a cog is loaded
    @commands.Cog.listener()
    async def on_cog_load(self, cog):
        logger.info(f"Cog {cog.qualified_name} loaded")