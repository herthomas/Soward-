import wavelink
import asyncio

from services.logging import logger



running = False
async def on_node(bot):
    global running
    while not bot.is_ready():
        logger.info("Waiting for bot to be ready to connect to Lavalink")
        await asyncio.sleep(1)
    if running:
        await wavelink.Pool.reconnect()
        return logger.info("Reconnected to Lavalink nodes")
    running = True
    
    nodes = [
        wavelink.Node(uri="http://localhost:6969", password="6969", retries=1)
    ]
    await wavelink.Pool.connect(
        nodes=nodes,
        client=bot
    )
    logger.info(f"Connected to Lavalink with {len(nodes)} nodes")
