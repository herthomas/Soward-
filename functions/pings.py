import discord.http
import requests
import discord
from connections.database import get_connection
from discord.ext import commands
from time import time

from services.logging import logger

from cache.cache import cache as cache_module

from core.Bot import AutoShardedBot
import wavelink

from time import time
from connections.database import get_connection

connection = None

async def database() -> int:
    global connection
    try:
        if connection is None or connection.is_closed():
            connection = await get_connection()
        start_time = time()
        await connection.fetch("SELECT 1")
        return round(((time() - start_time) * 1000),2)
    except Exception as e:
        logger.error(f"Database ping failed: {e}")
        return -1



def bot(bot:AutoShardedBot) -> int:
    return round(bot.latency*1000,2)

def api() -> float:
    """
    This function is used to check the latency of the API.
    """
    start_time = time()
    try:
        requests.get(discord.http.Route.BASE)
        return round(((time() - start_time) * 1000),2)
    except Exception as e:
        return -1

def cache() -> float:
    """
    This function is used to check the latency of the cache.
    """
    start_time = time()
    try:
        cache_module.guilds.get(str(1), str(1))
        return round(((time() - start_time) * 1000),3)
    except Exception as e:
        return -1

def google() -> float:
    """
    This function is used to check the latency of the google.
    """
    start_time = time()
    try:
        requests.get("https://www.google.com")
        return round(((time() - start_time) * 1000),2)
    except Exception as e:
        return -1
    
def youtube() -> float:
    """
    This function is used to check the latency of the youtube.
    """
    start_time = time()
    try:
        requests.get("https://www.youtube.com")
        return round(((time() - start_time) * 1000),2)
    except Exception as e:
        return -1
    
    
def github() -> float:
    """
    This function is used to check the latency of the github.
    """
    start_time = time()
    try:
        requests.get("https://www.github.com")
        return round(((time() - start_time) * 1000),2)
    except Exception as e:
        return -1
    

def shard(bot:AutoShardedBot, shard_id:int) -> int:
    """
    This function is used to check the latency of the shard.
    """
    shard_info = bot.get_shard(shard_id)
    return round(shard_info.latency*1000,2)

def shards(bot:AutoShardedBot) -> dict:
    """
    This function is used to check the latency of the shards.
    """
    for shard in bot.shards:
        shard = bot.get_shard(shard)
        latency = shard.latency
    return {str(shard[0]): round(shard[1]*1000,2) for shard in bot.latencies}