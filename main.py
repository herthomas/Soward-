import asyncio
import discord
import discord.http
import fastapi
import uvicorn
from core.Bot import AutoShardedBot

from settings.config import BotConfigClass
BotConfig = BotConfigClass()

# discord.http.Route.BASE = "http://localhost:3000/api/v9"

bot = AutoShardedBot()

from services.logging import logger
import traceback


async def main():
    try:
        from modules.sync import loadDataBase
        from modules.cache import load_cache
        from api import api
        await loadDataBase()
        await load_cache()
        await bot.load_extension("cogs")

        tasks = []

        async def start_bot():
            try:
                await bot.start(BotConfig.TOKEN, reconnect=True)
            except KeyboardInterrupt:
                logger.error("Bot has been stopped")
            except discord.RateLimited as e:
                logger.error(f"Bot is rate limited. Retrying in {e.retry_after} seconds")
            except discord.LoginFailure as e:
                logger.error(f"Login failed. {e}")
            except discord.HTTPException as e:
                retry_after = e.response.headers.get('Retry-After', 'N/A')
                logger.error(f"Bot is rate limited. Retrying in {retry_after} seconds")
                if retry_after == 'N/A':
                    return
                # Log detailed information about the request that caused the rate limit
                logger.error(f"Rate limit details: {e.response.status} {e.response.reason}")
                logger.error(f"Response headers: {e.response.headers}")
                logger.error(f"Response text: {e.status} {e.text}")
                await asyncio.sleep(int(retry_after))

        async def start_api():
            try:
                api_config = uvicorn.Config(
                    api.app,
                    host="0.0.0.0",
                    port=8008
                )
                server = uvicorn.Server(api_config)
                await server.serve()
            except Exception as e:
                logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
        try:
            tasks.append(asyncio.create_task(start_api()))
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
        try:
            tasks.append(asyncio.create_task(start_bot()))
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main())