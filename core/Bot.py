import discord
from discord.ext import commands
import inspect
import datetime

from settings import config
BotConfig = config.BotConfigClass()

from cache.cache import cache

from themes import color
from services.logging import logger

from databases import guilds_log as guilds_log_db
import databases
from themes import emoji,urls
import importlib
import asyncio
import wavelink
from collections import defaultdict
import time

def get_function_args(func):
    signature = inspect.signature(func)
    return [param.name for param in signature.parameters.values()]



class Log:
    def __init__(self, bot):
        self.bot = bot
        self.log_error_type = [type for type in get_function_args(guilds_log_db.get) if type not in ['guild_id', 'id', 'enabled', 'updated_at', 'created_at']]
        
        # Initialize timeout_data to track the number of logs sent per guild and their log queues
        self.timeout_data = defaultdict(lambda: {"count": 0, "last_log_time": 0, "queue": None})
    
    async def send(self, guild: discord.Guild, type: str, embed: discord.Embed = None, content: str = None):
        type = type.lower() + "_channel_id"
        guilds_log_cache = cache.guilds_log.get(str(guild.id))
        
        if not guilds_log_cache or not guilds_log_cache.get('enabled'):
            return
        
        if type not in self.log_error_type:
            return
        
        channel_id = guilds_log_cache.get(type)
        if not channel_id:
            return
        
        channel = guild.get_channel(int(channel_id))
        if not channel:
            return
        
        if not embed and not content:
            return
        
        if not embed:
            embed = discord.Embed(
                title="Error",
                description=content,
                color=color.red
            )
        
        # Initialize the queue for the guild if it doesn't exist
        guild_data = self.timeout_data[guild.id]
        if guild_data["queue"] is None:
            guild_data["queue"] = asyncio.Queue()
            asyncio.create_task(self.process_queue(guild))  # Start a background task to process the queue
        
        # Add both the channel and the embed (log entry) to the queue
        await guild_data["queue"].put((channel, embed))
    
    async def process_queue(self, guild: discord.Guild):
        guild_data = self.timeout_data[guild.id]
        queue = guild_data["queue"]
        
        while True:
            # Fetch the next (channel, embed) tuple from the queue
            channel, embed = await queue.get()
            
            current_time = time.time()
            
            # Reset count if more than 60 seconds have passed since the last log
            if current_time - guild_data["last_log_time"] > 60:
                guild_data["count"] = 0
            
            # If more than 5 logs have been sent within 60 seconds, introduce a 5-second delay
            if guild_data["count"] >= 20:
                await asyncio.sleep(5)
            
            # Try to send the log
            try:
                await channel.send(embed=embed)
                guild_data["count"] += 1
                guild_data["last_log_time"] = current_time
            except Exception as e:
                logger.error(f"Error in Log.process_queue: {e}")
            
            # Mark the task as done
            queue.task_done()
    
    async def wait_for_all_queues(self):
        # Wait until all queues are empty before proceeding (useful for shutdowns or graceful exits)
        tasks = []
        for guild_id, guild_data in self.timeout_data.items():
            if guild_data["queue"] is not None:
                tasks.append(guild_data["queue"].join())
        await asyncio.gather(*tasks)


        
class antinuke_log:
    def __init__(self, bot):
        self.bot = bot
        self.log_error_type = [type for type in get_function_args(guilds_log_db.get) if type not in ['guild_id','id','enabled','updated_at','created_at']]
    
    async def send(self,guild:discord.Guild,type:str,embed:discord.Embed=None,content:str=None):
        type = type.lower()+ "_channel_id"
        guilds_log_cache = cache.guilds_log[str(guild.id)]
        if not guilds_log_cache.get('enabled'):
            return
        
        if type not in self.log_error_type:
            return
        

        channel_id = guilds_log_cache.get(type)

        if not channel_id:
            return
        
        channel = guild.get_channel(int(channel_id))
        if not channel:
            return

        if not embed and not content:
            return
        if not embed:
            embed = discord.Embed(
                title="Error",
                description=content,
                color=color.red
            )
        
        try:
            await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in Log.error: {e}")

class EmojiManager:
    def __init__(self, default_emoji="❓"):
        self.default_emoji = default_emoji

    def __getattr__(self, item):
        # Check if the emoji exists as a variable in the emoji module
        return getattr(emoji, item, self.default_emoji)

class AutoShardedBot(commands.AutoShardedBot):
    def __init__(self, *arg, **kwargs):
        super().__init__(command_prefix=self.get_prefix,
                        case_insensitive=True,
                        intents=discord.Intents.all(),
                        status=discord.Status.dnd,
                        strip_after_prefix=True,
                        sync_commands_debug=True,
                        sync_commands=True,
                        help_command=None,
                        shard_count=BotConfig.SHARD_COUNT,
                        allowed_mentions=discord.AllowedMentions(everyone=False,replied_user=False,roles=False)
                        )
        self.developer:discord.User = self.user
        self.log = Log(self)
        self.users_data = config.users
        self.emoji = emoji # EmojiManager()
        self.cache = cache
        self.BotConfig = BotConfig
        self.channels = config.channels
        self.database = databases
        self.antinuke_log = antinuke_log(self)
        self.urls = urls
        self.variables = {
                        "{user}": "The user's name",
                        "{user.id}": "The user's id",
                        "{user.tag}": "The user's tag",
                        "{user.mention}": "The user's mention",
                        "{user.avatar}": "The user's avatar",
                        "{user.created_at}": "The user's account creation date",
                        "{user.joined_at}": "The user's join date",
                        "{guild}": "The server name",
                        "{server}": "The server name",
                        "{server.id}": "The server id",
                        "{server.icon}": "The server icon",
                        "{guild.id}": "The server id",
                        "{guild.icon}": "The server icon",
                        "{guild.owner}": "The server owner",
                        "{guild.owner.id}": "The server owner id",
                        "{time}": "The current time",
                        "{member.count}": "The server member count"
                    }
        self.VERSION = '1.0.0'
        self.start_time = datetime.datetime.now(tz=datetime.timezone.utc)
    


    
    async def reload(self):
        importlib.reload(config)
        importlib.reload(emoji)
        importlib.reload(urls)
        importlib.reload(databases)
        self.users_data = config.users
        self.channels = config.channels
        self.BotConfig = config.BotConfigClass()
        self.urls = urls
        self.emoji = EmojiManager()
        self.database = databases



    
    async def get_prefix(self, message: discord.Message):
            default_prefix = str(BotConfig.PREFIX)
            if message.guild:
                guild_id = str(message.guild.id)                
                if cache.users.get(str(message.author.id),{}).get('no_prefix',False) == True and cache.users.get(str(message.author.id),{}).get('no_prefix_subscription',False) == True:
                    if guild_id in cache.guilds:
                        guild_cache = cache.guilds[guild_id]
                        prefix = guild_cache.get('prefix', default_prefix)
                        return commands.when_mentioned_or(prefix, '')(self, message)
                    else:
                        return commands.when_mentioned_or(default_prefix, '')(self, message)
                else:
                    if guild_id in cache.guilds:
                        guild_cache = cache.guilds[guild_id]
                        prefix = guild_cache.get('prefix', default_prefix)
                        return commands.when_mentioned_or(prefix)(self, message)
                    else:
                        return commands.when_mentioned_or(default_prefix)(self, message)
            else:
                return commands.when_mentioned_or(default_prefix)(self, message)