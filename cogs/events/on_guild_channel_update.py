import datetime,asyncio,discord
from discord.ext import commands

from services.logging import logger
from cogs.checks import checks

from cache.cache import cache


from themes import color

from core.Bot import AutoShardedBot


class on_guild_channel_update(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot

    async def channel_update_log(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        try:
            guilds_log_cache = cache.guilds_log.get(str(after.guild.id))
            if not guilds_log_cache:
                return 
            if not guilds_log_cache.get('enabled'):
                return logger.warning(f"Guild {after.guild.name} has logging disabled")
            channel_id = guilds_log_cache.get('channel_update_channel_id')
            if not channel_id:
                return logger.warning(f"Channel ID not found for channel update log in {after.guild.name}")
            
            async def check_entry():
                async for entry in after.guild.audit_logs(limit=1,action=discord.AuditLogAction.channel_update):
                    if entry.target.id == after.id:
                        return entry
            entry = await check_entry()
            if entry:
                user = entry.user.mention
                user_id = entry.user.id
                reason = entry.reason
            else:
                user = "Unknown"
                user_id = "Unknown"
                reason = "Unknown"

            embed = discord.Embed(
                title=f'#{after.name} has been updated',
                description=f'**__Channel:__** {after.mention}\n**__Channel Name:__** `#{after.name}`\n**__Channel ID:__** `{after.id}`\n**__Channel Type:__** {after.type}{f'\n**__Channel Category:__** {after.category.mention}\n**__Channel Category ID:__** `{after.category.id}`' if after.category else ''}\n**__Channel Created At:__** <t:{int(after.created_at.timestamp())}>\n\n**__Updated By:__** {user}\n**__Updated By ID:__** `{user_id}`\n**__Reason:__** `{reason}`\n\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}>\n{'-'*50}',
                color=color.white
            )
            if before.name != after.name:
                embed.add_field(name="Name changed",value=f"**Before:** {before.name}\n**After:** {after.name}")
            if isinstance(before, discord.TextChannel) and before.topic != after.topic:
                embed.add_field(name="Topic changed",value=f"**Before:** {before.topic}\n**After:** {after.topic}")
            if before.category != after.category:
                embed.add_field(name="Category changed",value=f"**Before:** {before.category.mention}\n**After:** {after.category.mention}")
            try:
                if before.slowmode_delay != after.slowmode_delay:
                    embed.add_field(name="Slowmode changed",value=f"**Before:** {before.slowmode_delay}\n**After:** {after.slowmode_delay}")
            except:
                pass
            if before.nsfw != after.nsfw:
                embed.add_field(name="NSFW changed",value=f"**Before:** {before.nsfw}\n**After:** {after.nsfw}")
            if before.position != after.position:
                embed.add_field(name="Position changed",value=f"**Before:** {before.position}\n**After:** {after.position}")
            if isinstance(before, discord.VoiceChannel) and isinstance(after, discord.VoiceChannel):
                embed.add_field(name="Bitrate changed",value=f"**Before:** {before.bitrate}\n**After:** {after.bitrate}")
            if isinstance(before, discord.VoiceChannel) and before.user_limit != after.user_limit:
                embed.add_field(name="User limit changed",value=f"**Before:** {before.user_limit}\n**After:** {after.user_limit}")
            if before.overwrites != after.overwrites:
                embed.add_field(name="Overwrites changed",value=f"**Before:** {before.overwrites}\n**After:** {after.overwrites}")
            embed.set_footer(text=f'Channel ID: {after.id}')
            embed.set_thumbnail(url=after.guild.icon.url if after.guild.icon else None)
            await self.bot.log.send(guild=after.guild,embed=embed,type=f"channel_update")
        except Exception as e:
            logger.error(f"Error in on_guild_channel_update.channel_update_log: {e}")

    update_channel_timeouts = {}

    async def anti_channel_update_module(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        channel = after

        # check if the channel is a j2channel

        if self.bot.cache.j2c.get(str(channel.guild.id),{}).get(str(channel.id),None):
            return logger.warning(f"Channel {channel.name} is a j2channel in {channel.guild.name}")

        
        try:
            anti_nuke_cache = self.bot.cache.antinuke_settings.get(str(channel.guild.id))
            if not anti_nuke_cache:
                return 
            if not anti_nuke_cache.get('enabled'):
                return logger.warning(f"Guild {channel.guild.name} has antinuke disabled")
            
            if not anti_nuke_cache.get('anti_channel_update'):
                return logger.warning(f"Anti Channel Update is disabled in {channel.guild.name}")
            
            async def check_entry():
                async for entry in channel.guild.audit_logs(limit=1,action=discord.AuditLogAction.channel_update):
                    if entry.target.id == channel.id:
                        return entry
            entry = await check_entry()

            if entry:
                deletor = entry.user
                if deletor == self.bot.user:
                    return logger.warning(f"Channel {channel.name} was deleted by the bot in {channel.guild.name}")
            else:
                return logger.warning(f"Channel {channel.name} was deleted by unknown in {channel.guild.name}")
            
            anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(str(channel.guild.id),{}).get(str(deletor.id),{})
            if anti_nuke_bypass_cache.get('anti_channel_update'):
                return logger.warning(f"User {deletor} is bypassed from Anti Channel Update in {channel.guild.name}")
            
            if deletor.top_role.position >= channel.guild.me.top_role.position:
                return logger.warning(f"User {deletor} has higher or equal role than the bot in {channel.guild.name}")
            if deletor == channel.guild.owner or await checks.check_is_owner_raw(deletor,channel.guild):
                return logger.warning(f"User {deletor} is the owner of the guild in {channel.guild.name}")
            
            # =============================================

            if str(channel.guild.id) not in self.update_channel_timeouts:
                self.update_channel_timeouts[str(channel.guild.id)] = {}
            if str(deletor.id) not in self.update_channel_timeouts.get(str(channel.guild.id)):
                self.update_channel_timeouts[str(channel.guild.id)][str(deletor.id)] = {
                    'count': 0,
                    'created_at': datetime.datetime.now()
                }
            self.update_channel_timeouts[str(channel.guild.id)][str(deletor.id)]['count'] += 1
            self.update_channel_timeouts[str(channel.guild.id)][str(deletor.id)]['created_at'] = datetime.datetime.now()


            if str(channel.guild.id) in self.update_channel_timeouts:
                if self.update_channel_timeouts.get(str(channel.guild.id)):
                    if self.update_channel_timeouts.get(str(channel.guild.id),{}).get(str(deletor.id)):
                        if (self.update_channel_timeouts.get(str(channel.guild.id),{}).get(str(deletor.id),{}).get('count') >= anti_nuke_cache.get('anti_channel_update_limit',1)
                            and
                            self.update_channel_timeouts.get(str(channel.guild.id),{}).get(str(deletor.id),{}).get('created_at') >= (datetime.datetime.now() - datetime.timedelta(seconds=60))
                            ):
                            # getting action for the user
                            action = anti_nuke_cache.get('anti_channel_update_punishment')

                            async def send_notify_to_user(user:discord.Member,embed:discord.Embed):
                                try:
                                    await user.send(embed=embed)
                                except:
                                    logger.warning(f"Could not send message to {user} in {channel.guild.name}")

                            if action == 'ban':
                                try:
                                    embed = discord.Embed(
                                        title="You have been banned",
                                        description=f"**__Guild:__ `{channel.guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Channel Update\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=channel.guild.icon.url if channel.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deletor,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Banned",
                                        description=f"**__User__**: {deletor.mention}\n**__ID__**: `{deletor.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Channel Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deletor.display_avatar.url)
                                    await channel.guild.ban(deletor,reason="Banned by Antinuke System: Anti Channel Update")
                                    await self.bot.antinuke_log.send(guild=channel.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_channel_update.anti_channel_update_module: {e}")
                            elif action == 'kick':
                                try:
                                    embed = discord.Embed(
                                        title="You have been kicked",
                                        description=f"**__Guild:__ `{channel.guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Channel Update\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=channel.guild.icon.url if channel.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deletor,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Kicked",
                                        description=f"**__User__**: {deletor.mention}\n**__ID__**: `{deletor.id}`\n**__Action__**: `Kick`\n**__Reason__**: Anti Channel Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deletor.display_avatar.url)
                                    await channel.guild.kick(deletor,reason="Kicked by Antinuke System: Anti Channel Update")
                                    await self.bot.antinuke_log.send(guild=channel.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_channel_update.anti_channel_update_module: {e}")
                            elif action == 'warn':
                                try:
                                    embed = discord.Embed(
                                        title="You have been warned",
                                        description=f"**__Guild:__ `{channel.guild.name}`**\n**Details:** ```\nYou have been warned for Anti Channel Update\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=channel.guild.icon.url if channel.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deletor,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Warned",
                                        description=f"**__User__**: {deletor.mention}\n**__ID__**: `{deletor.id}`\n**__Action__**: `Warn`\n**__Reason__**: Anti Channel Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deletor.display_avatar.url)
                                    await self.bot.antinuke_log.send(guild=channel.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_channel_update.anti_channel_update_module: {e}")
                            elif action == 'mute':
                                try:
                                    embed = discord.Embed(
                                        title="You have been muted",
                                        description=f"**__Guild:__ `{channel.guild.name}`**\n**__Action:__** `Mute`\n**__Reason:__** Anti Channel Update\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=channel.guild.icon.url if channel.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deletor,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Muted",
                                        description=f"**__User__**: {deletor.mention}\n**__ID__**: `{deletor.id}`\n**__Action__**: `Mute`\n**__Reason__**: Anti Channel Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deletor.display_avatar.url)
                                    try:
                                        await deletor.edit(roles=[],reason="Muted by Antinuke System: Anti Channel Update")
                                    except:
                                        pass
                                    await deletor.timeout(datetime.timedelta(days=1),reason="Muted by Antinuke System: Anti Channel Update")
                                    await self.bot.antinuke_log.send(guild=channel.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_channel_update.anti_channel_update_module: {e}")
                            else:
                                return logger.warning(f"Invalid action {action} in {channel.guild.name}")

                            if action != 'warn':
                            # reset the timeout
                                if str(channel.guild.id) in self.update_channel_timeouts:
                                    if str(deletor.id) in self.update_channel_timeouts.get(str(channel.guild.id)):
                                        self.update_channel_timeouts[str(channel.guild.id)][str(deletor.id)] = {
                                            'count': 0,
                                            'created_at': datetime.datetime.now()
                                        }
                            return

        except Exception as e:
            logger.error(f"Error in on_guild_channel_update.anti_channel_update_module: {e}")
                        
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        try:
            asyncio.create_task(self.anti_channel_update_module(before, after))
        except Exception as e:
            pass
        try:
            asyncio.create_task(self.channel_update_log(before, after))
        except Exception as e:
            pass