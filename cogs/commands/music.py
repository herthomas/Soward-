import discord
from discord.ext import commands
import wavelink

from cogs.checks import checks

import databases.guilds
import databases.music
from services.logging import logger

from themes import color

import traceback,sys

import asyncio

from core.Bot import AutoShardedBot

from modules.ui import create_music_controller_image

import datetime
import databases

import re

def is_link(text):
    # Define a regex pattern to match URLs
    pattern = re.compile(
        r'^(https?:\/\/)?'  # Match the protocol (http or https)
        r'((([A-Za-z0-9-]+\.)+[A-Za-z]{2,})|'  # Match domain (e.g. example.com)
        r'((\d{1,3}\.){3}\d{1,3}))'  # Match IP address (e.g. 192.168.0.1)
        r'(:\d+)?(\/\S*)?$',  # Optional port and resource path
        re.IGNORECASE
    )
    return re.match(pattern, text) is not None


def convert_ms_to_beautiful_time(ms:int):
    try:
        seconds = ms // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        weeks, days = divmod(days, 7)
        months, weeks = divmod(weeks, 4)

        time = ""
        if months:
            time += f"{months}M "
        if weeks:
            time += f"{weeks}W "
        if days:
            time += f"{days}D "
        if hours:
            time += f"{hours}h "
        if minutes:
            time += f"{minutes}m "
        if seconds:
            time += f"{seconds}s"
        return time
    except Exception as e:
        logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
        return "Unknown"

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot:AutoShardedBot = bot
        class cog_info:
            name =  "Music"
            category = "Main"
            description =  "Music commands"
            hidden =  False
            emoji = self.bot.emoji.MUSIC or "❓"
        self.cog_info = cog_info

    @commands.hybrid_command(
        name="play",
        aliases=["p"],
        help="Play music in the voice channel.",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def play(self, ctx: commands.Context, *, search: str):
        try:
            if ctx.interaction:
                await ctx.defer()

            music_data = self.bot.cache.music.get(str(ctx.guild.id),{})
            if music_data:
                if music_data.get("music_setup_channel_id",None):
                    # send to use the setuped channel to play music
                    embed = discord.Embed(
                        description=f"Send anything in the channel <#{music_data.get('music_setup_channel_id',None)}> to play music.",
                        color=color.red
                    )
                    embed.set_author(
                        name=ctx.guild.name,
                        icon_url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url,
                        url=self.bot.urls.WEBSITE
                    )
                    embed.set_footer(text=f"Use /resetmusic to reset the setup of music")
                    return await ctx.reply(embed=embed)

            # Check if the user is in a voice channel
            if not ctx.author.voice:
                await ctx.reply("You need to be in a voice channel to use this command.")
                return
            
            try:
                # Check if the user is in a voice channel
                if not ctx.author.voice:
                    return await ctx.reply(f"{self.bot.emoji.ERROR} | You need to be in a voice channel to use this command.",delete_after=10)
                destination = ctx.author.voice.channel
                # Connect to the voice channel if not already connected
                if not ctx.guild.voice_client:
                    vc: wavelink.Player = await destination.connect(cls=wavelink.Player,timeout=60,self_deaf=True)
                    vc.inactive_timeout = 10
                else:
                    vc: wavelink.Player = ctx.guild.voice_client
                    # if the bot is another vc and not playing anything then move to the new vc
                    if vc.channel.id != destination.id:
                        if not vc.current:
                            await vc.move_to(destination)
                        else:
                            return await ctx.reply(f"{self.bot.emoji.ERROR} | The bot is already playing in another voice channel.",delete_after=10)
                
                if ctx.author.voice.channel.id != vc.channel.id:
                    return await ctx.reply(f"{self.bot.emoji.ERROR} | You need to be in the same voice channel as the bot to use this command.",delete_after=10)

                users_no_prefix_subscription = self.bot.cache.users.get(str(ctx.author.id),{}).get('no_prefix_subscription',None)
                guilds_subscription = self.bot.cache.guilds.get(str(ctx.guild.id),{}).get('subscription','free')

                if not users_no_prefix_subscription and guilds_subscription == 'free':
                    if is_link(search):
                        return await ctx.reply(
                            embed=discord.Embed(
                                description="You can't play music using links in the free subscription.",
                                color=color.red
                            ),
                            view=discord.ui.View().add_item(
                                discord.ui.Button(
                                    label="Upgrade Subscription",
                                    style=discord.ButtonStyle.url,
                                    url=self.bot.urls.SUPPORT_SERVER,
                                    emoji=self.bot.emoji.SUPPORT
                                )
                            )
                        )

                # Use the new search methood correctly
                result = await wavelink.Playable.search(search, source=wavelink.TrackSource.YouTube)
                if not result:
                    return await ctx.reply(f"{self.bot.emoji.ERROR} | No results found for the search query.",delete_after=10)
                
                track = result[0]


                if not vc.current:
                    if guilds_subscription == 'free':
                        default_volume = 80
                    else:
                        default_volume = self.bot.cache.music.get(str(ctx.guild.id),{}).get('default_volume',80)
                    await vc.play(track,volume=default_volume)
                    await self.send_music_controls(ctx.guild,update_attachments=True,command_channel=ctx.channel)
                    await ctx.reply(f"{self.bot.emoji.PLAYING} | Now playing: {track.title}")
                else:
                    if len(vc.queue) >= 10:
                        return await ctx.reply(f"{self.bot.emoji.LIMIT} | You can only add up to 10 tracks in the queue.",delete_after=10)
                    await vc.queue.put_wait(track)
                    await self.send_music_controls(ctx.guild,command_channel=ctx.channel)
                    await ctx.reply(f"{self.bot.emoji.CREATE} | Added to the queue: {track.title}")
            except TimeoutError:
                return await ctx.reply(embed=discord.Embed(
                    description="The bot took too long to connect to the voice channel.\nPlease try again after changing the voice channel region.",
                    color=color.red
                ),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    music_controller_view_timeout_data = {} # {guild_id: datetime.datetime}

    async def select_filter_callback(self, interaction: discord.Interaction):
        try:
            vc: wavelink.Player = interaction.guild.voice_client
            if not vc:
                return await interaction.response.send_message(
                    embed=discord.Embed(description="The bot is not connected to any voice channel.", color=color.red),
                    ephemeral=True,
                    delete_after=10
                )

            if not interaction.user.voice:
                return await interaction.response.send_message(
                    embed=discord.Embed(description="You need to be in a voice channel to use this button.", color=color.red),
                    ephemeral=True,
                    delete_after=10
                )

            if vc.channel != interaction.user.voice.channel:
                return await interaction.response.send_message(
                    embed=discord.Embed(description="You need to be in the same voice channel as the bot to use this button.", color=color.red),
                    ephemeral=True,
                    delete_after=10
                )

            # Rate limiting
            if self.music_controller_view_timeout_data.get(interaction.guild.id, None) and \
                    datetime.datetime.now() - self.music_controller_view_timeout_data[interaction.guild.id] < datetime.timedelta(seconds=10):
                return await interaction.response.send_message(
                    embed=discord.Embed(description=f"{self.bot.emoji.TIME} | Clicking too fast.", color=color.red),
                    ephemeral=True,
                    delete_after=10
                )

            self.music_controller_view_timeout_data[interaction.guild.id] = datetime.datetime.now()
            await interaction.response.defer()

            # Get the selected filter
            selected_filter = interaction.data["values"][0]

            if selected_filter == "none":
                await vc.set_filters(None,seek=True)
                await self.send_music_controls(interaction.guild, update_attachments=True)
                await interaction.followup.send(f"{self.bot.emoji.SUCCESS} | Filter has been removed.")
            else:
                await self.send_music_controls(interaction.guild, update_attachments=True)
                await interaction.followup.send(f"{self.bot.emoji.SUCCESS} | Filter has been set to {selected_filter}.")

        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    async def volume_down_button_callback(self,interaction:discord.Interaction):
        print(self.music_controller_view_timeout_data)
        try:
            vc: wavelink.Player = interaction.guild.voice_client
            if not vc:
                return await interaction.response.send_message(embed=discord.Embed(description="The bot is not connected to any voice channel.", color=color.red), ephemeral=True,delete_after=10)
            if not interaction.user.voice:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in a voice channel to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if vc.channel != interaction.user.voice.channel:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in the same voice channel as the bot to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if self.music_controller_view_timeout_data.get(interaction.guild.id,None) and datetime.datetime.now() - self.music_controller_view_timeout_data.get(interaction.guild.id,datetime.datetime.now()) < datetime.timedelta(seconds=10):
                return await interaction.response.send_message(embed=discord.Embed(description=f"{self.bot.emoji.TIME} | Clicking too fast.", color=color.red), ephemeral=True,delete_after=10)
            self.music_controller_view_timeout_data[interaction.guild.id] = datetime.datetime.now()
            if vc.volume <= 0:
                return await interaction.response.send_message(embed=discord.Embed(description="The volume is already at the minimum.", color=color.red), ephemeral=True,delete_after=10)
            await interaction.response.defer()
            await vc.set_volume(vc.volume - 10)
            await self.send_music_controls(interaction.guild,update_attachments=True)
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
    
    async def stop_button_callback(self,interaction:discord.Interaction):
        try:
            vc: wavelink.Player = interaction.guild.voice_client
            if not vc:
                return await interaction.response.send_message(embed=discord.Embed(description="The bot is not connected to any voice channel.", color=color.red), ephemeral=True,delete_after=10)
            
            if not interaction.user.voice:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in a voice channel to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if vc.channel != interaction.user.voice.channel:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in the same voice channel as the bot to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if self.music_controller_view_timeout_data.get(interaction.guild.id,None) and datetime.datetime.now() - self.music_controller_view_timeout_data.get(interaction.guild.id,datetime.datetime.now()) < datetime.timedelta(seconds=10):
                return await interaction.response.send_message(embed=discord.Embed(description=f"{self.bot.emoji.TIME} | Clicking too fast.", color=color.red), ephemeral=True,delete_after=10)
            self.music_controller_view_timeout_data[interaction.guild.id] = datetime.datetime.now()
            await interaction.response.defer()
            vc.queue.clear()
            await vc.stop()
            await vc.disconnect()
            await self.send_music_controls(interaction.guild,end=True)
            temp_message = await interaction.followup.send(f"{self.bot.emoji.STOP} | Player has been stopped. By {interaction.user.mention}")
            await asyncio.sleep(10)
            try:
                await temp_message.delete()
            except:
                pass
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
    
    async def pause_resume_button_callback(self,interaction:discord.Interaction):
        try:
            vc: wavelink.Player = interaction.guild.voice_client
            if not vc:
                return await interaction.response.send_message(embed=discord.Embed(description="The bot is not connected to any voice channel.", color=color.red), ephemeral=True,delete_after=10)
            if not interaction.user.voice:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in a voice channel to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if vc.channel != interaction.user.voice.channel:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in the same voice channel as the bot to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if self.music_controller_view_timeout_data.get(interaction.guild.id,None) and datetime.datetime.now() - self.music_controller_view_timeout_data.get(interaction.guild.id,datetime.datetime.now()) < datetime.timedelta(seconds=10):
                return await interaction.response.send_message(embed=discord.Embed(description=f"{self.bot.emoji.TIME} | Clicking too fast.", color=color.red), ephemeral=True,delete_after=10)
            self.music_controller_view_timeout_data[interaction.guild.id] = datetime.datetime.now()
            await interaction.response.defer()
            if vc.paused:
                await vc.pause(False)
                await self.send_music_controls(interaction.guild)
                temp_message = await interaction.followup.send(f"{self.bot.emoji.PLAYING} | Player has been resumed. By {interaction.user.mention}")
                await asyncio.sleep(10)
                try:
                    await temp_message.delete()
                except:
                    pass
            else:
                await vc.pause(True)
                await self.send_music_controls(interaction.guild)
                temp_message = await interaction.followup.send(f"{self.bot.emoji.PAUSED} | Player has been paused. By {interaction.user.mention}")
                await asyncio.sleep(10)
                try:
                    await temp_message.delete()
                except:
                    pass
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
    
    async def skip_button_callback(self,interaction:discord.Interaction):
        try:
            vc: wavelink.Player = interaction.guild.voice_client
            if not vc:
                return await interaction.response.send_message(embed=discord.Embed(description="The bot is not connected to any voice channel.", color=color.red), ephemeral=True,delete_after=10)
            
            if not interaction.user.voice:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in a voice channel to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if vc.channel != interaction.user.voice.channel:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in the same voice channel as the bot to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if self.music_controller_view_timeout_data.get(interaction.guild.id,None) and datetime.datetime.now() - self.music_controller_view_timeout_data.get(interaction.guild.id,datetime.datetime.now()) < datetime.timedelta(seconds=10):
                return await interaction.response.send_message(embed=discord.Embed(description=f"{self.bot.emoji.TIME} | Clicking too fast.", color=color.red), ephemeral=True,delete_after=10)
            self.music_controller_view_timeout_data[interaction.guild.id] = datetime.datetime.now()
            await interaction.response.defer()
            if vc.queue or vc.autoplay != wavelink.AutoPlayMode.disabled:
                await vc.skip(force=True)
                temp_message = await interaction.followup.send(f"{self.bot.emoji.SUCCESS} | Skipped the current track. By {interaction.user.mention}")
                await asyncio.sleep(10)
                try:
                    await temp_message.delete()
                except:
                    pass
            else:
                temp_message = await interaction.followup.send(f"{self.bot.emoji.ERROR} | The queue is empty.")
                await asyncio.sleep(10)
                try:
                    await temp_message.delete()
                except:
                    pass
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
    
    async def volume_up_button_callback(self,interaction:discord.Interaction):
        try:
            vc: wavelink.Player = interaction.guild.voice_client
            if not vc:
                return await interaction.response.send_message(embed=discord.Embed(description="The bot is not connected to any voice channel.", color=color.red), ephemeral=True,delete_after=10)
            if not interaction.user.voice:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in a voice channel to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if vc.channel != interaction.user.voice.channel:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in the same voice channel as the bot to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if self.music_controller_view_timeout_data.get(interaction.guild.id,None) and datetime.datetime.now() - self.music_controller_view_timeout_data.get(interaction.guild.id,datetime.datetime.now()) < datetime.timedelta(seconds=10):
                return await interaction.response.send_message(embed=discord.Embed(description=f"{self.bot.emoji.TIME} | Clicking too fast.", color=color.red), ephemeral=True,delete_after=10)
            self.music_controller_view_timeout_data[interaction.guild.id] = datetime.datetime.now()
            if vc.volume >= 100:
                return await interaction.response.send_message(embed=discord.Embed(description="The volume is already at the maximum.", color=color.red), ephemeral=True,delete_after=10)
            await interaction.response.defer()
            await vc.set_volume(vc.volume + 10)
            await self.send_music_controls(interaction.guild,update_attachments=True)
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
    
    async def loop_toggle_callback(self,interaction:discord.Interaction):
        try:
            vc: wavelink.Player = interaction.guild.voice_client
            if not vc:
                return await interaction.response.send_message(embed=discord.Embed(description="The bot is not connected to any voice channel.", color=color.red), ephemeral=True,delete_after=10)
            if not interaction.user.voice:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in a voice channel to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if vc.channel != interaction.user.voice.channel:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in the same voice channel as the bot to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if self.music_controller_view_timeout_data.get(interaction.guild.id,None) and datetime.datetime.now() - self.music_controller_view_timeout_data.get(interaction.guild.id,datetime.datetime.now()) < datetime.timedelta(seconds=10):
                return await interaction.response.send_message(embed=discord.Embed(description=f"{self.bot.emoji.TIME} | Clicking too fast.", color=color.red), ephemeral=True,delete_after=10)
            self.music_controller_view_timeout_data[interaction.guild.id] = datetime.datetime.now()
            await interaction.response.defer()
            if vc.queue.mode == wavelink.QueueMode.loop:
                vc.queue.mode = wavelink.QueueMode.normal
                # await self.send_music_controls(interaction.guild,update_attachments=True)
                temp_message = await interaction.followup.send(f"{self.bot.emoji.SUCCESS} | Looping has been disabled. By {interaction.user.mention}")
                await asyncio.sleep(10)
                try:
                    await temp_message.delete()
                except:
                    pass
            else:
                vc.queue.mode = wavelink.QueueMode.loop
                # await self.send_music_controls(interaction.guild,update_attachments=True)
                temp_message = await interaction.followup.send(f"{self.bot.emoji.SUCCESS} | Looping has been enabled. By {interaction.user.mention}")
                await asyncio.sleep(10)
                try:
                    await temp_message.delete()
                except:
                    pass
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    async def autoplay_toggle_callback(self,interaction:discord.Interaction):
        try:
            vc: wavelink.Player = interaction.guild.voice_client
            if not vc:
                return await interaction.response.send_message(embed=discord.Embed(description="The bot is not connected to any voice channel.", color=color.red), ephemeral=True,delete_after=10)
            if not interaction.user.voice:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in a voice channel to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if vc.channel != interaction.user.voice.channel:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in the same voice channel as the bot to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if self.music_controller_view_timeout_data.get(interaction.guild.id,None) and datetime.datetime.now() - self.music_controller_view_timeout_data.get(interaction.guild.id,datetime.datetime.now()) < datetime.timedelta(seconds=10):
                return await interaction.response.send_message(embed=discord.Embed(description=f"{self.bot.emoji.TIME} | Clicking too fast.", color=color.red), ephemeral=True,delete_after=10)
            self.music_controller_view_timeout_data[interaction.guild.id] = datetime.datetime.now()
            await interaction.response.defer()
            if vc.autoplay == wavelink.AutoPlayMode.disabled:
                vc.autoplay = wavelink.AutoPlayMode.enabled
                # await self.send_music_controls(interaction.guild,update_attachments=True)
                temp_message = await interaction.followup.send(f"{self.bot.emoji.SUCCESS} | Autoplay has been enabled. By {interaction.user.mention}")
                await asyncio.sleep(10)
                try:
                    await temp_message.delete()
                except:
                    pass
            else:
                vc.autoplay = wavelink.AutoPlayMode.disabled
                # await self.send_music_controls(interaction.guild,update_attachments=True)
                temp_message = await interaction.followup.send(f"{self.bot.emoji.SUCCESS} | Autoplay has been disabled. By {interaction.user.mention}")
                await asyncio.sleep(10)
                try:
                    await temp_message.delete()
                except:
                    pass
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    async def set_volume_button_callback(self,interaction:discord.Interaction):
        try:
            vc: wavelink.Player = interaction.guild.voice_client
            if not vc:
                return await interaction.response.send_message(embed=discord.Embed(description="The bot is not connected to any voice channel.", color=color.red), ephemeral=True,delete_after=10)
            if not interaction.user.voice:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in a voice channel to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if vc.channel != interaction.user.voice.channel:
                return await interaction.response.send_message(embed=discord.Embed(description="You need to be in the same voice channel as the bot to use this button.", color=color.red), ephemeral=True,delete_after=10)
            if self.music_controller_view_timeout_data.get(interaction.guild.id,None) and datetime.datetime.now() - self.music_controller_view_timeout_data.get(interaction.guild.id,datetime.datetime.now()) < datetime.timedelta(seconds=10):
                return await interaction.response.send_message(embed=discord.Embed(description=f"{self.bot.emoji.TIME} | Clicking too fast.", color=color.red), ephemeral=True,delete_after=10)
            self.music_controller_view_timeout_data[interaction.guild.id] = datetime.datetime.now()
            
            class set_volume_modal(discord.ui.Modal,title="Set Volume"):
                new_volume_field = discord.ui.TextInput(
                    label="Volume",
                    min_length=1,
                    max_length=3,
                    required=True,
                    default=str(vc.volume),
                    placeholder="Volume (0-100)",
                    style=discord.TextStyle.short
                )
                bot = self.bot
                send_music_controls = self.send_music_controls
                async def on_submit(self,interaction:discord.Interaction):
                    try:
                        vc: wavelink.Player = interaction.guild.voice_client
                        if not vc:
                            return await interaction.response.send_message(embed=discord.Embed(description="The bot is not connected to any voice channel.", color=color.red), ephemeral=True,delete_after=10)
                        if not interaction.user.voice:
                            return await interaction.response.send_message(embed=discord.Embed(description="You need to be in a voice channel to use this button.", color=color.red), ephemeral=True,delete_after=10)
                        if vc.channel != interaction.user.voice.channel:
                            return await interaction.response.send_message(embed=discord.Embed(description="You need to be in the same voice channel as the bot to use this button.", color=color.red), ephemeral=True,delete_after=10)
                        
                        try:
                            volume = int(self.new_volume_field.value)
                        except:
                            return await interaction.response.send_message(embed=discord.Embed(description="Invalid volume value.", color=color.red), ephemeral=True,delete_after=10)
                        
                        if not 0 <= volume <= 100:
                            return await interaction.response.send_message(embed=discord.Embed(description="Volume must be between 0 and 100.", color=color.red), ephemeral=True,delete_after=10)
                        
                        await interaction.response.defer()
                        await vc.set_volume(volume)
                        await self.send_music_controls(interaction.guild,update_attachments=True)
                        filled_blocks = volume // 10
                        empty_blocks = 10 - filled_blocks
                        text = "🟩" * filled_blocks + "⬜" * empty_blocks
                        temp_message = await interaction.followup.send(f"`{text}`")
                        await asyncio.sleep(5)
                        try:
                            await temp_message.delete()
                        except:
                            pass
                    except Exception as e:
                        logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            await interaction.response.send_modal(set_volume_modal())
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    
    manual_controller_data = {} # {guild_id: discord.Message}  # Store the controller message for each guild
    async def send_music_controls(self, guild: discord.Guild,update_attachments:bool=False,end:bool=False,command_channel:discord.TextChannel=None):
        try:
            if str(guild.id) not in self.manual_controller_data:
                self.manual_controller_data[str(guild.id)] = {}

            music_data = self.bot.cache.music.get(str(guild.id),{})

            if end:
                controller_message = self.manual_controller_data.get(str(guild.id),None)
                if music_data:
                    if music_data.get("music_setup_channel_id",None):
                        try:
                            command_channel = guild.get_channel(music_data.get("music_setup_channel_id",None))
                            try:
                                controller_message = await command_channel.fetch_message(music_data.get("music_setup_message_id",None))
                            except:
                                logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
                                controller_message = None
                            embed = discord.Embed(
                                color=color.aqua
                            )
                            embed.set_author(
                                name=guild.name,
                                icon_url=guild.icon.url if guild.icon else self.bot.user.display_avatar.url,
                                url=self.bot.urls.WEBSITE
                            )
                            embed.set_image(url=self.bot.urls.DEFAULT_MUSIC_BANNER)
                            embed.set_footer(text="Type anything in this channel to start Playing Music")
                            if controller_message:
                                view = discord.ui.View().from_message(controller_message)
                                for item in view.children:
                                    item.disabled = True
                                await controller_message.edit(embed=embed,view=view,attachments=[])
                            else:
                                controller_message = await command_channel.send(embed=embed,view=None)
                                await databases.music.update(
                                    id=music_data.get('id'),
                                    music_setup_message_id=controller_message.id
                                )
                        except:
                            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
                    else:
                        if controller_message:
                            try:
                                embed = discord.Embed(
                                    title="Music Controller",
                                    description="The player has been stopped.",
                                    color=color.black
                                )
                                embed.set_footer(text="This message will be deleted in 10 seconds.")
                                if str(guild.id) in self.manual_controller_data:
                                    del self.manual_controller_data[str(guild.id)]
                                await controller_message.edit(embed=embed,delete_after=10,view=None,attachments=[])
                            except Exception as e:
                                logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
                else:
                    if controller_message:
                        try:
                            embed = discord.Embed(
                                title="Music Controller",
                                description="The player has been stopped.",
                                color=color.black
                            )
                            embed.set_footer(text="This message will be deleted in 10 seconds.")
                            if str(guild.id) in self.manual_controller_data:
                                del self.manual_controller_data[str(guild.id)]
                            await controller_message.edit(embed=embed,delete_after=10,view=None,attachments=[])
                        except Exception as e:
                            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
                return
            

            vc: wavelink.Player = guild.voice_client

            if not vc:
                return logger.error(f"Voice client not found for {guild.name}")


            query_embed = discord.Embed(
                title=f"{len(vc.queue)+1} tracks in queue",
                description="",
                color=color.black
            )
            if vc.current:
                cutted_title = vc.current.title[:50] + "..." if len(vc.current.title) > 50 else vc.current.title
                query_embed.description += f"**{self.bot.emoji.PLAYING if not vc.paused else self.bot.emoji.PAUSED} 1. [{cutted_title}]({self.bot.urls.SUPPORT_SERVER}) - `{convert_ms_to_beautiful_time(vc.current.length)}`**\n"
            for index, track in enumerate(vc.queue, start=2):
                cutted_title = track.title[:50] + "..." if len(track.title) > 50 else track.title
                query_embed.description += f"**{self.bot.emoji.QUEUE} {index}. [{cutted_title}]({self.bot.urls.SUPPORT_SERVER}) - `{convert_ms_to_beautiful_time(track.length)}`**\n"

            controller_embed = discord.Embed(
                title="Music Controller",
                description="",
                color=color.black
            )
            controller_embed.set_image(url="attachment://music_controller.png")
            if update_attachments:
                try:
                    music_controller_image = create_music_controller_image(
                        music_thumbnail_url=vc.current.artwork,
                        music_title=vc.current.title,
                        music_author=vc.current.author,
                        music_album=vc.current.album.name,
                        music_duration=vc.current.length,
                        current_position=vc.current.length * 0.05,
                        volume=vc.volume
                    )
                    if music_controller_image:
                        file = discord.File(music_controller_image, filename="music_controller.png")
                    else:
                        logger.error(f"Failed to create music controller image for {guild.name}")
                        file = None
                except:
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    file = None
            else:
                file = None
            # Send or update controller message
            embeds = [query_embed, controller_embed]


            async def get_controller_view():
                try:
                    view = discord.ui.View(timeout=None)
                    volume_down_button = discord.ui.Button(
                        emoji=self.bot.emoji.VOLUME_DOWN,
                        style=discord.ButtonStyle.gray,
                        row=0,
                        disabled=vc.volume <= 0
                    )
                    stop_button = discord.ui.Button(
                        emoji=self.bot.emoji.STOP,
                        style=discord.ButtonStyle.red,
                        row=0
                    )
                    pause_resume_button = discord.ui.Button(
                        emoji=self.bot.emoji.PAUSED if vc.paused else self.bot.emoji.RESUME,
                        style=discord.ButtonStyle.gray,
                        row=0
                    )
                    skip_button = discord.ui.Button(
                        emoji=self.bot.emoji.SKIP,
                        style=discord.ButtonStyle.gray,
                        row=0
                    )
                    volume_up_button = discord.ui.Button(
                        emoji=self.bot.emoji.VOLUME_UP,
                        style=discord.ButtonStyle.gray,
                        row=0,
                        disabled=vc.volume >= 100
                    )

                    autoplay_toggle = discord.ui.Button(
                        emoji=self.bot.emoji.AUTOPLAY,
                        style=discord.ButtonStyle.gray,
                        row=1
                    )

                    loop_toggle = discord.ui.Button(
                        emoji=self.bot.emoji.LOOP,
                        style=discord.ButtonStyle.gray,
                        row=1
                    )

                    set_volume_button = discord.ui.Button(
                        emoji=self.bot.emoji.MASTER_VOLUME,
                        style=discord.ButtonStyle.green,
                        row=1
                    )

                    volume_down_button.callback = lambda i: self.volume_down_button_callback(i)
                    stop_button.callback = lambda i: self.stop_button_callback(i)
                    pause_resume_button.callback = lambda i: self.pause_resume_button_callback(i)
                    skip_button.callback = lambda i: self.skip_button_callback(i)
                    volume_up_button.callback = lambda i: self.volume_up_button_callback(i)
                    loop_toggle.callback = lambda i: self.loop_toggle_callback(i)
                    autoplay_toggle.callback = lambda i: self.autoplay_toggle_callback(i)
                    set_volume_button.callback = lambda i: self.set_volume_button_callback(i)
                    view.add_item(volume_down_button)
                    view.add_item(stop_button)
                    view.add_item(pause_resume_button)
                    view.add_item(skip_button)
                    view.add_item(volume_up_button)
                    view.add_item(autoplay_toggle)
                    view.add_item(loop_toggle)
                    view.add_item(set_volume_button)
                    return view
                except Exception as e:
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return None



            controller_message = self.manual_controller_data.get(str(guild.id),None)
            if music_data:
                if music_data.get("music_setup_channel_id",None):
                    try:
                        command_channel = guild.get_channel(music_data.get("music_setup_channel_id",None))
                        try:
                            controller_message = await command_channel.fetch_message(music_data.get("music_setup_message_id",None))
                        except:
                            controller_message = None
                    except:
                        controller_message = None
            if not controller_message:
                try:
                    controller_message = await command_channel.send(embeds=embeds, file=file if file else None, view=await get_controller_view())
                    if music_data:
                        if music_data.get("music_setup_channel_id",None):
                            await databases.music.update(
                                id=music_data.get('id'),
                                music_setup_message_id=controller_message.id
                            )
                        else:
                            self.manual_controller_data[str(guild.id)] = controller_message
                    else:
                        self.manual_controller_data[str(guild.id)] = controller_message
                except Exception as e:
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return await command_channel.send(f"{self.bot.emoji.ERROR} | Failed to send the controller message.", delete_after=10)
            else:
                try:
                    if file:
                        await controller_message.edit(embeds=embeds, attachments=[file], view=await get_controller_view())
                    else:
                        await controller_message.edit(embeds=embeds, view=await get_controller_view())
                except Exception as e:
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return await command_channel.send(f"{self.bot.emoji.ERROR} | Failed to edit the controller message.", delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")     

    @commands.Cog.listener(name="on_message")
    async def on_message(self,message:discord.Message):
        if message.channel.id in [1289263302152552458]:
            pass
            # await self.play_music(message.guild,message.content,message.author,message.channel)


    @commands.hybrid_command(
        name="pause",
        help="Pause the player.",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def pause(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.guild.voice_client
        if vc:
            if ctx.interaction:
                await ctx.defer()
            if not ctx.author.voice:
                return await ctx.send(f"{self.bot.emoji.ERROR} | You need to be in a voice channel to use this command.", delete_after=10)
            if vc.channel != ctx.author.voice.channel:
                return await ctx.send(f"{self.bot.emoji.ERROR} | You need to be in the same voice channel as the bot to use this command.", delete_after=10)
            if vc.paused:
                await ctx.send("The player is already paused.")
                return
            await vc.pause(True)
            await self.send_music_controls(ctx.guild)
            await ctx.reply(f"{self.bot.emoji.PAUSED} | Player has been paused.")
        else:
            await ctx.send(f"{self.bot.emoji.ERROR} | The bot is not connected to any voice channel.", delete_after=10)

    @commands.hybrid_command(
        name="resume",
        help="Resume the player.",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def resume(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.guild.voice_client
        if vc:
            if ctx.interaction:
                await ctx.defer()
            if not ctx.author.voice:
                return await ctx.send(f"{self.bot.emoji.ERROR} | You need to be in a voice channel to use this command.", delete_after=10)
            if vc.channel != ctx.author.voice.channel:
                return await ctx.send(f"{self.bot.emoji.ERROR} | You need to be in the same voice channel as the bot to use this command.", delete_after=10)
            if not vc.paused:
                await ctx.send("The player is already playing.")
                return
            await vc.pause(False)
            await self.send_music_controls(ctx.guild)
            await ctx.reply(f"{self.bot.emoji.PLAYING} | Resumed the player.")
        else:
            await ctx.send(f"{self.bot.emoji.ERROR} | The bot is not connected to any voice channel.", delete_after=10)

    @commands.command(name="skip")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def skip(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.guild.voice_client

        # Check if the user is in a voice channel
        if not ctx.author.voice:
            return await ctx.send(f"{self.bot.emoji.ERROR} | You need to be in a voice channel to use this command.", delete_after=10)

        # Check if the bot is in a voice channel
        if not vc:
            return await ctx.send(f"{self.bot.emoji.ERROR} | The bot is not connected to any voice channel.", delete_after=10)
        
        # Check if the bot and user are in the same voice channel
        if vc and vc.channel != ctx.author.voice.channel:
            return await ctx.send(f"{self.bot.emoji.ERROR} | You need to be in the same voice channel as the bot to use this command.", delete_after=10)

        if ctx.interaction:
            await ctx.defer()

        # Check if there is a track currently playing or paused
        if vc.playing or vc.paused:
            # Skip the current track
            await vc.stop()  # This triggers the `on_wavelink_track_end` listener to handle the next track
            await ctx.reply(f"{self.bot.emoji.SUCCESS} | Skipped the current track.")
        else:
            await ctx.send(f"{self.bot.emoji.ERROR} | No track is currently playing or paused.", delete_after=10)
    
    @commands.hybrid_command(
        name="loop",
        help="Loop the current track.",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def loop(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.guild.voice_client
        
        if not vc:
            return await ctx.send(f"{self.bot.emoji.ERROR} | The bot is not connected to any voice channel.", delete_after=10)

        # Check if the user is in a voice channel
        if not ctx.author.voice:
            return await ctx.send(f"{self.bot.emoji.ERROR} | You need to be in a voice channel to use this command.", delete_after=10)
        
        # Check if the bot and user are in the same voice channel
        if vc.channel != ctx.author.voice.channel:
            return await ctx.send(f"{self.bot.emoji.ERROR} | You need to be in the same voice channel as the bot to use this command.", delete_after=10)

        if ctx.interaction:
            await ctx.defer()

        # Toggle loop mode between 'normal' and 'loop'
        if vc.queue.mode == wavelink.QueueMode.loop:
            vc.queue.mode = wavelink.QueueMode.normal
            await ctx.reply(f"{self.bot.emoji.SUCCESS} | Looping has been disabled.")
        else:
            vc.queue.mode = wavelink.QueueMode.loop
            await ctx.reply(f"{self.bot.emoji.SUCCESS} | Looping has been enabled.")


    @commands.hybrid_command(
        name="queue",
        aliases=["q","tracks","track"],
        help="Show the queue of the player.",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def queue(self, ctx: commands.Context):
        try:
            vc: wavelink.Player = ctx.guild.voice_client
            if vc:
                if ctx.interaction:
                    await ctx.defer()
                async def get_embed():
                    embed = discord.Embed(
                        title="Track Queue",
                        description="",
                        color=color.black
                    )
                    if vc.current:
                        cuted_title = vc.current.title[:50] + "..." if len(vc.current.title) > 50 else vc.current.title
                        embed.description += f"**{self.bot.emoji.PAUSED if vc.paused else self.bot.emoji.PLAYING} 1. [{cuted_title}]({self.bot.urls.SUPPORT_SERVER}) - `{convert_ms_to_beautiful_time(vc.current.length)}`**\n"
                    for index, track in enumerate(vc.queue, start=2):
                        cuted_title = track.title[:50] + "..." if len(track.title) > 50 else track.title
                        embed.description += f"**{self.bot.emoji.QUEUE} {index}. [{cuted_title}]({self.bot.urls.SUPPORT_SERVER}) - `{convert_ms_to_beautiful_time(track.length)}`**\n"
                    return embed

                timeout_time = 60
                cancled = False
                def reset_timeout_time():
                    nonlocal timeout_time
                    timeout_time = 60
                
                async def get_view(disabled=False):
                    view = discord.ui.View()
                    reset_timeout_time()
                    options = []
                    for index,queue in enumerate(vc.queue):
                        try:
                            cuted_title = queue.title[:50] + "..." if len(queue.title) > 50 else queue.title
                            options.append(discord.SelectOption(label=cuted_title,value=str(index),emoji=self.bot.emoji.QUEUE,description=f"Length: {convert_ms_to_beautiful_time(queue.length)}"))
                        except Exception as e:
                            logger.error(f"Error in file {__file__}: {e}")

                    select_to_delete_queue = discord.ui.Select(
                        placeholder="Select a Queue to Delete",
                        options=options,
                        disabled=len(options) == 0
                    )
                    select_to_delete_queue.callback = lambda i: select_to_delete_queue_callback(i)
                    if len(options) !=0:
                        view.add_item(select_to_delete_queue)

                    if disabled:
                        for item in view.children:
                            item.disabled = True
                    return view
                
                async def select_to_delete_queue_callback(interaction: discord.Interaction):
                    try:
                        if interaction.user.id != ctx.author.id:
                            return await interaction.response.send_message(embed=discord.Embed(description="You can't use this button.", color=color.red), ephemeral=True,delete_after=5)
                        await interaction.response.defer()
                        print(interaction.data)
                        track_index = int(interaction.data["values"][0])
                        if track_index == None:
                            return await interaction.edit_original_response(embed=discord.Embed(description="Invalid track selected.", color=color.red))
                        if not vc.queue:
                            return await interaction.edit_original_response(embed=discord.Embed(description="The queue is empty.", color=color.red))
                        if len(vc.queue) < track_index-1:
                            return await interaction.edit_original_response(embed=discord.Embed(description="Invalid track selected.", color=color.red))
                        vc.queue.delete(track_index)
                        await interaction.message.edit(embed=await get_embed(), view=await get_view())
                    except Exception as e:
                        logger.error(f"Error in file {__file__}: {e}")


                message = await ctx.send(embed=await get_embed(), view=await get_view())

                while not cancled:
                    try:
                        timeout_time -= 1
                        if timeout_time <= 0:
                            await message.edit(view=await get_view(disabled=True))
                            break
                        await asyncio.sleep(1)
                    except Exception as e:
                        logger.error(f"Error in file {__file__}: {e}")
            else:
                await ctx.send(f"{self.bot.emoji.ERROR} | The bot is not connected to any voice channel.", delete_after=10)
        except Exception as e:
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    @commands.hybrid_command(
        name="volume",
        aliases=["vol","v"],
        help="Get or set the volume of the player.",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def volume(self, ctx: commands.Context, volume: int=None):
        vc: wavelink.Player = ctx.guild.voice_client
        if vc:
            if ctx.interaction:
                await ctx.defer()
            if not ctx.author.voice:
                return await ctx.send(f"{self.bot.emoji.ERROR} | You need to be in a voice channel to use this command.", delete_after=10)
            if vc.channel != ctx.author.voice.channel:
                return await ctx.send(f"{self.bot.emoji.ERROR} | You need to be in the same voice channel as the bot to use this command.", delete_after=10)
            if not volume:
                await ctx.send(f"Current volume: {vc.volume}")
            else:
                if volume < 0 or volume > 100:
                    return await ctx.send(f"{self.bot.emoji.LIMIT} | Volume must be between 0 and 100.", delete_after=10)
                    
                await vc.set_volume(volume)
                filled_blocks = volume // 10
                empty_blocks = 10 - filled_blocks
                text = "🟩" * filled_blocks + "⬜" * empty_blocks
                await ctx.reply(f"`{text}`")
                await self.send_music_controls(ctx.guild,update_attachments=True)
        else:
            await ctx.send(f"{self.bot.emoji.ERROR} | The bot is not connected to any voice channel.", delete_after=10)

    @commands.hybrid_command(
        name="stop",
        help="Stop the player and disconnect the bot from the voice channel.",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def stop(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.guild.voice_client
        manually_disconnected = False
        if ctx.interaction:
            await ctx.defer()
        if not vc:
            try:
                # Check if the bot is connected to a voice channel
                if ctx.guild.me.voice:
                    await ctx.guild.me.move_to(None)
                    manually_disconnected = True
            except Exception as e:
                logger.error(f"Error in file {__file__}: {e}")
        if vc:
            if not ctx.author.voice:
                return await ctx.send(f"{self.bot.emoji.ERROR} | You need to be in a voice channel to use this command.", delete_after=10)
            if vc.channel != ctx.author.voice.channel:
                return await ctx.send(f"{self.bot.emoji.ERROR} | You need to be in the same voice channel as the bot to use this command.", delete_after=10)
            vc.queue.clear()
            await vc.stop()
            try:
                await ctx.send(f"{self.bot.emoji.STOP} | Player has been stopped.", delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__}: {e}")
            await vc.disconnect()
            await self.send_music_controls(ctx.guild,end=True)
        elif manually_disconnected:
            await ctx.send(f"{self.bot.emoji.SUCCESS} | The bot has been disconnected.", delete_after=10)
        elif not vc and not manually_disconnected:
            await ctx.send(f"{self.bot.emoji.ERROR} | The bot is not connected to any voice channel.", delete_after=10)
    
    @commands.hybrid_command(
        name="current",
        aliases=["nowplaying"],
        help="Show the current playing track.",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def current(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.guild.voice_client
        if vc:
            if ctx.interaction:
                await ctx.defer()
            if not vc.current:
                await ctx.send("No track is currently playing.")
                return
            await ctx.send(f"**{self.bot.emoji.PLAYING} : {vc.current.title}** __by__ `{vc.current.author}`")
        else:
            await ctx.send("The bot is not connected to any voice channel.", delete_after=10)

    #autoplay
    @commands.hybrid_command(
        name="autoplay",
        help="Toggle autoplay mode.",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5, per=30, type=commands.BucketType.user)
    async def autoplay(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.guild.voice_client
        if vc:
            if ctx.interaction:
                await ctx.defer()
            if not ctx.author.voice:
                return await ctx.send(f"{self.bot.emoji.ERROR} | You need to be in a voice channel to use this command.", delete_after=10)
            if vc.channel != ctx.author.voice.channel:
                return await ctx.send(f"{self.bot.emoji.ERROR} | You need to be in the same voice channel as the bot to use this command.", delete_after=10)
            if vc.autoplay == wavelink.AutoPlayMode.disabled:
                vc.autoplay = wavelink.AutoPlayMode.enabled
                await ctx.reply(f"{self.bot.emoji.SUCCESS} | Autoplay has been enabled.")
            else:
                vc.autoplay = wavelink.AutoPlayMode.disabled
                await ctx.reply(f"{self.bot.emoji.SUCCESS} | Autoplay has been disabled.")
        else:
            await ctx.send(f"{self.bot.emoji.ERROR} | The bot is not connected to any voice channel.", delete_after=10)
    

    async def music_setup_function(self,message:discord.Message):
        try:
            # this cuntion will work like play command
            try:
                await message.delete()
            except:
                logger.warning(f"Failed to delete the message in {message.guild.name} for music function")

            if not message.author.voice:
                return await message.channel.send(f"{self.bot.emoji.ERROR} | You need to be in a voice channel to use this command.", delete_after=10)
                # destination = ctx.author.voice.channel
                # # Connect to the voice channel if not already connected
                # if not ctx.guild.voice_client:
                #     vc: wavelink.Player = await destination.connect(cls=wavelink.Player,timeout=60)
                #     vc.inactive_timeout = 10
                # else:
                #     vc: wavelink.Player = ctx.guild.voice_client
                #     # if the bot is another vc and not playing anything then move to the new vc
                #     if vc.channel.id != destination.id:
                #         if not vc.current:
                #             await vc.move_to(destination)
                #         else:
                #             return await ctx.reply(f"{self.bot.emoji.ERROR} | The bot is already playing in another voice channel.",delete_after=10)
            
            if not message.guild.voice_client:
                vc: wavelink.Player = await message.author.voice.channel.connect(cls=wavelink.Player,timeout=60,self_deaf=True)
                vc.inactive_timeout = 10
            else:
                vc: wavelink.Player = message.guild.voice_client
                if vc.channel != message.author.voice.channel:
                    if not vc.current:
                        await vc.move_to(message.author.voice.channel)
                    else:
                        return await message.channel.send(f"{self.bot.emoji.ERROR} | The bot is already playing in another voice channel.",delete_after=5)

            if not vc.connected:
                return await message.channel.send(f"{self.bot.emoji.ERROR} | Failed to connect to the voice channel.",delete_after=5)
            
            search = message.content

            if not search:
                return await message.channel.send(f"{self.bot.emoji.ERROR} | Please provide a search query.",delete_after=5)
            
            users_no_prefix_subscription = self.bot.cache.users.get(str(message.author.id),{}).get('no_prefix_subscription',None)
            guilds_subscription = self.bot.cache.guilds.get(str(message.guild.id),{}).get('subscription','free')
            if not users_no_prefix_subscription and guilds_subscription == 'free':
                if is_link(search):
                    return await message.channel.send(
                        embed=discord.Embed(
                            description="You can't play music using links in the free subscription.",
                            color=color.red
                        ),
                        view=discord.ui.View().add_item(
                            discord.ui.Button(
                                label="Upgrade Subscription",
                                style=discord.ButtonStyle.url,
                                url=self.bot.urls.SUPPORT_SERVER,
                                emoji=self.bot.emoji.SUPPORT
                            )
                        )
                    )
                
            result = await wavelink.Playable.search(search, source=wavelink.TrackSource.YouTube)
            if not result:
                await vc.disconnect()
                return await message.channel.send(f"{self.bot.emoji.ERROR} | No tracks found.",delete_after=5)
            
            track = result[0]
            if not vc.current:
                if guilds_subscription == 'free':
                    default_volume = 80
                else:
                    default_volume = self.bot.cache.music.get(str(message.guild.id),{}).get('default_volume',80)
                await vc.play(track,volume=default_volume)
                await self.send_music_controls(message.guild,update_attachments=True)
                await message.channel.send(f"{self.bot.emoji.SUCCESS} | Playing: {track.title}",delete_after=5)
            else:
                if len(vc.queue) >= 10:
                    return await message.channel.send(f"{self.bot.emoji.ERROR} | The queue is full.",delete_after=5)
                await vc.queue.put_wait(track)
                await self.send_music_controls(message.guild)
                await message.channel.send(f"{self.bot.emoji.SUCCESS} | Added to queue: {track.title}",delete_after=5)
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    
    @commands.hybrid_group(
        name="music",
        help="Music Related Functions",
        invoke_without_command=True,
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3,per=60,type=commands.BucketType.user)
    async def music_group(self, ctx: commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'administrator'):
                return 
            
            embed = discord.Embed(
                title="Music Config Commands",
                description=f"Here are the list of commands\n\n",
                color=color.green
            )

            if hasattr(ctx.command,'commands'):
                for command in ctx.command.commands:
                    embed.description += f"**`{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` - {command.help}**\n"
            else:
                embed.description += f"**`{self.bot.BotConfig.PREFIX}{ctx.command.name}` - {ctx.command.help}**\n"

            embed.set_footer(
                text=f"Developed by Soward Development",
                icon_url=self.bot.user.display_avatar.url
            )
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
    
    @music_group.command(
        name="setup",
        help="Setup the music channel",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=60,type=commands.BucketType.guild)
    async def music_setup(self, ctx: commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'administrator'):
                return 
            
            if ctx.interaction:
                await ctx.defer(ephemeral=True)
            
            music_data = self.bot.cache.music.get(str(ctx.guild.id),{})
            if not music_data:
                await databases.music.insert(guild_id=ctx.guild.id)
                music_data = self.bot.cache.music.get(str(ctx.guild.id),{})
            if music_data.get("music_setup_channel_id",None):
                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} | The music channel is already Exists in <#{music_data.get('music_setup_channel_id')}>",
                        color=color.red
                    ).set_footer(text=f"Use /music reset to reset the music channel.",icon_url=self.bot.user.display_avatar.url),
                    delete_after=10
                )
            
            waiting_message = await ctx.send(f"{self.bot.emoji.LOADING} | Creating the music channel...")
            try:
                music_setup_channel = await ctx.guild.create_text_channel(name="🎵-music-channel")
            except:
                logger.error(f"Traceback: {traceback.format_exc()}")
                if not ctx.interaction:
                    return await waiting_message.edit(content=f"{self.bot.emoji.ERROR} | Failed to create the music channel.",delete_after=10)
                else:
                    return await ctx.send(f"{self.bot.emoji.ERROR} | Failed to create the music channel.")
            await databases.music.update(
                id=music_data.get('id'),
                music_setup_channel_id=music_setup_channel.id
            )
            await waiting_message.edit(content=f"{self.bot.emoji.SUCCESS} | Music channel has been created in <#{music_setup_channel.id}>")
            await self.send_music_controls(ctx.guild,end=True)
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
    
    @music_group.command(
        name="reset",
        help="Reset the music channel",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=60,type=commands.BucketType.guild)
    async def music_reset(self, ctx: commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'administrator'):
                return 
            
            if ctx.interaction:
                await ctx.defer(ephemeral=True)
            
            music_data = self.bot.cache.music.get(str(ctx.guild.id),{})
            if not music_data:
                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} | The music channel is not exists.",
                        color=color.red
                    ).set_footer(text=f"Use /music setup to setup the music channel.",icon_url=self.bot.user.display_avatar.url),
                    delete_after=10
                )
            
            if not music_data.get("music_setup_channel_id",None):
                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} | The music channel is not exists.",
                        color=color.red
                    ).set_footer(text=f"Use /music setup to setup the music channel.",icon_url=self.bot.user.display_avatar.url),
                    delete_after=10
                )
            
            waiting_message = await ctx.send(f"{self.bot.emoji.LOADING} | Deleting the music channel...")
            try:
                music_setup_channel = ctx.guild.get_channel(music_data.get("music_setup_channel_id"))
                if music_setup_channel:
                    await music_setup_channel.delete()
            except:
                logger.error(f"Traceback: {traceback.format_exc()}")
                if not ctx.interaction:
                    return await waiting_message.edit(content=f"{self.bot.emoji.ERROR} | Failed to delete the music channel.",delete_after=10)
                else:
                    return await ctx.send(f"{self.bot.emoji.ERROR} | Failed to delete the music channel.")
            await databases.music.update(
                id=music_data.get('id'),
                music_setup_channel_id=""
            )
            await waiting_message.edit(content=f"{self.bot.emoji.SUCCESS} | Music channel has been deleted.")
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
    
    @music_group.command(
        name="settings",
        help="Show the music settings",
        with_app_command=True,
        aliases=["config","setting"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=4,per=60,type=commands.BucketType.guild)
    async def music_settings(self, ctx: commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'administrator'):
                return 
            
            if ctx.interaction:
                await ctx.defer(ephemeral=True)
            music_data = self.bot.cache.music.get(str(ctx.guild.id),{})
            if not music_data:
                await databases.music.insert(guild_id=ctx.guild.id)
                music_data = self.bot.cache.music.get(str(ctx.guild.id),{})
            
            async def get_embed():
                music_data = self.bot.cache.music.get(str(ctx.guild.id),{})
                embed = discord.Embed(
                    title="Music Settings",
                    description="Configure the music settings for your server",
                    color=color.green
                )
                embed.add_field(
                    name="Default Volume",
                    value=f"`{music_data.get('default_volume',80) if music_data.get('default_volume') else '80'}`",
                    inline=True
                )
                embed.add_field(
                    name="Music Channel",
                    value=f"<#{music_data.get('music_setup_channel_id')}>" if music_data.get('music_setup_channel_id') else "`No music channel set`",
                    inline=True
                )
                embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.display_avatar.url)
                embed.set_author(
                    name=ctx.guild.name,
                    icon_url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url,
                    url=self.bot.urls.WEBSITE
                )
                embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url)
                return embed
            
            timeout_time = 200
            cancled = False
            def reset_timeout(timeout:int=200):
                nonlocal timeout_time
                timeout_time = timeout

            
            async def get_view(disabled=False):
                try:
                    reset_timeout()
                    music_data = self.bot.cache.music.get(str(ctx.guild.id),{})
                    view = discord.ui.View(timeout=200)
                    default_volume_button = discord.ui.Button(
                        label="Set Default Volume",
                        style=discord.ButtonStyle.primary,
                        emoji=self.bot.emoji.MASTER_VOLUME,
                        row=0
                    )
                    music_channels = []
                    if music_data.get('music_setup_channel_id'):
                        try:
                            music_channel = ctx.guild.get_channel(music_data.get('music_setup_channel_id'))
                            if music_channel:
                                music_channels.append(music_channel)
                        except:
                            logger.error(f"Traceback: {traceback.format_exc()}")
                    music_channel_Select = discord.ui.ChannelSelect(
                        placeholder="Select the music channel",
                        min_values=1,
                        max_values=1,
                        row=1,
                        channel_types=[discord.ChannelType.text],
                        default_values=music_channels if music_channels else None
                    )
                    cancle_button = discord.ui.Button(
                        label="Cancel",
                        style=discord.ButtonStyle.gray,
                        emoji=self.bot.emoji.CANCLED,
                        row=0
                    )
                    default_volume_button.callback = lambda i: default_volume_button_callback(i)
                    music_channel_Select.callback = lambda i: music_channel_Select_callback(i)
                    cancle_button.callback = lambda i: cancle_button_callback(i)
                    view.add_item(default_volume_button)
                    view.add_item(music_channel_Select)
                    view.add_item(cancle_button)
                    if disabled:
                        for item in view.children:
                            item.disabled = True
                    return view
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                    return None
            
            async def default_volume_button_callback(interaction:discord.Interaction):
                try:
                    if ctx.author.id != interaction.user.id:
                        return await interaction.response.send_message(embed=discord.Embed(description="You can't interact with this button",color=color.red),ephemeral=True)
                    guilds_subscription = self.bot.cache.guilds.get(str(message.guild.id),{}).get('subscription','free')

                    if guilds_subscription == 'free':
                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You can't change the default volume in free subscription.",
                                color=color.red
                            ),
                            view=discord.ui.View().add_item(
                                discord.ui.Button(
                                    label="Buy Subscription",
                                    style=discord.ButtonStyle.link,
                                    url=self.bot.urls.SUPPORT_SERVER,
                                    emoji=self.bot.emoji.SUPPORT
                                )
                            ),
                            ephemeral=True
                        )
                    
                    class set_default_volume_modal(discord.ui.Modal,title="Set Default Volume"):
                        new_volume = discord.ui.TextInput(
                            label="Enter the new volume",
                            placeholder="Enter the new volume",
                            required=True,
                            style=discord.TextStyle.short,
                            row=0,
                            default=str(self.bot.cache.music.get(str(ctx.guild.id),{}).get('default_volume',80) if self.bot.cache.music.get(str(ctx.guild.id),{}).get('default_volume') else "80")
                        )
                        bot = self.bot
                        async def on_submit(self, interaction: discord.Interaction):
                            try:
                                if ctx.author.id != interaction.user.id:
                                    return await interaction.response.send_message(embed=discord.Embed(description="You can't interact with this button",color=color.red),ephemeral=True)
                                try:
                                    new_volume = int(self.new_volume.value)
                                except:
                                    return await interaction.response.send_message(embed=discord.Embed(description="Invalid number",color=color.red),ephemeral=True,delete_after=5)
                                if 0 < new_volume > 100:
                                    return await interaction.response.send_message(embed=discord.Embed(description="The number must be between 0 and 100",color=color.red),ephemeral=True,delete_after=5)
                                await interaction.response.defer()
                                music_data = self.bot.cache.music.get(str(ctx.guild.id),{})
                                print(f"Updating the default volume to {new_volume}")
                                await databases.music.update(
                                    id=music_data.get('id'),
                                    guild_id=ctx.guild.id,
                                    default_volume=new_volume
                                )
                                print(f"Updated the default volume to {new_volume}")
                                await interaction.message.edit(embed=await get_embed(),view=await get_view())
                            except Exception as e:
                                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}")
                    await interaction.response.send_modal(set_default_volume_modal())
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

            async def music_channel_Select_callback(interaction:discord.Interaction):
                try:
                    if ctx.author.id != interaction.user.id:
                        return await interaction.response.send_message(embed=discord.Embed(description="You can't interact with this button",color=color.red),ephemeral=True)
                    await interaction.response.defer()
                    music_data = self.bot.cache.music.get(str(ctx.guild.id),{})
                    channel = interaction.data['values']
                    await databases.music.update(
                        id=music_data.get('id'),
                        guild_id=ctx.guild.id,
                        music_setup_channel_id=channel[0]
                    )
                    await interaction.message.edit(embed=await get_embed(),view=await get_view())
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

            async def cancle_button_callback(interaction:discord.Interaction):
                try:
                    if ctx.author.id != interaction.user.id:
                        return await interaction.response.send_message(embed=discord.Embed(description="You can't interact with this button",color=color.red),ephemeral=True)
                    await interaction.response.defer()
                    nonlocal cancled
                    cancled = True
                    await interaction.message.edit(embed=await get_embed(),view=await get_view(disabled=True))
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

            embed = await get_embed()
            view = await get_view()
            message = await ctx.send(embed=embed,view=view)

            while not cancled:
                timeout_time -= 1
                if timeout_time <= 0:
                    await message.edit(embed=await get_embed(),view=await get_view(disabled=True))
                    break
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")


