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
class Wavelink(commands.Cog):
    def __init__(self, bot):
        self.bot:AutoShardedBot = bot
    
        self.MusicCog = self.bot.get_cog("Music")

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        logger.warning(f"Node {payload.node.uri} is ready!")

    @commands.Cog.listener()
    async def on_wavelink_node_closed(self, node: wavelink.Node, disconnected: list[wavelink.Player]):
        logger.warning(f"Node {node.uri} has been closed and cleaned-up. Disconnected players: {len(disconnected)}")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
        logger.warning(f"Track {payload.track} has started playing on player {payload.player.guild.name}")

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, payload: wavelink.TrackExceptionEventPayload):
        logger.error(f"An exception occurred while playing track {payload.track} on player {payload.player.guild.name}: {payload.exception}")

    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, payload: wavelink.TrackStuckEventPayload):
        logger.error(f"Track {payload.track} got stuck on player {payload.player.guild.name}")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        try:
            logger.info(f"Track end event received for track: {payload.track.title if payload.track else 'Unknown'}")

            if not payload.player:
                return logger.error(f"Player not found for {payload.player}")
            
            if payload.player.autoplay != wavelink.AutoPlayMode.disabled:
                for i in range(5):
                    if payload.player.current:
                        break
                    await asyncio.sleep(1)
                return await self.MusicCog.send_music_controls(guild=payload.player.guild, update_attachments=True)

            # Check if the queue is empty
            if payload.player.queue.is_empty and not payload.player.queue.mode == wavelink.QueueMode.loop:
                # If the queue is empty but the player is still playing, log it
                if payload.player.current:
                    logger.info(f"Queue is empty, but the player is still playing {payload.player.current.title}")
                    return
                
                # Disconnect if there's nothing left to play
                await payload.player.disconnect()
                logger.info(f"Queue is empty. Disconnected from {payload.player.guild.name}.")
                await self.MusicCog.send_music_controls(guild=payload.player.guild, end=True)
            else:
                try:
                    next_track = payload.player.queue.get()  # Get the next track from the queue
                except wavelink.exceptions.QueueEmpty:
                    await payload.player.disconnect()
                    await self.MusicCog.send_music_controls(guild=payload.player.guild, end=True)
                    return
                await payload.player.play(next_track)
                logger.info(f"Playing next track: {next_track.title}")
                await self.MusicCog.send_music_controls(guild=payload.player.guild, update_attachments=True)
        except Exception as e:
            logger.error(f"Error in track end handler: {traceback.format_exc()}")
    
    @commands.Cog.listener()
    async def on_wavelink_stats_update(self, payload: wavelink.StatsEventPayload):
        logger.warning(f"Stats for node {payload.node.uri} has been updated: {payload.stats}")

    @commands.Cog.listener()
    async def on_wavelink_player_update(self, payload: wavelink.PlayerUpdateEventPayload):
        logger.warning(f"Player {payload.player.guild.name} has been updated: {payload.state}")

    @commands.Cog.listener()
    async def on_wavelink_inactive_player(self, player: wavelink.Player) -> None:
        await player.channel.send(f"The player has been inactive for `{player.inactive_timeout}` seconds. Goodbye!")
        # await player.disconnect()

