import os
import dotenv

dotenv.load_dotenv(dotenv_path='./secrets/.env',override=True)

class BotConfigClass():
    TOKEN = os.getenv("TOKEN")
    PREFIX = os.getenv("PREFIX")
    SHARD_COUNT = int(os.getenv("SHARD_COUNT")) if os.getenv("SHARD_COUNT") else 1

class urls():
    gif_api_base = "https://api.tenor.com/v1/search"
    gif_api_key = "GET_YOUR_OWN_API_KEY"


class channels:
    report_channel = 1284958525906485319
    guild_join_webhook = "https://discord.com/api/webhooks/111111111111111111111/GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
    guild_leave_webhook = "https://discord.com/api/webhooks/111111111111111111111/GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"

    shards_log_webhook = "https://discord.com/api/webhooks/111111111111111111111/GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"

class users:
    developer = 1058254151810830357
    root = [1058254151810830357]

class Types:
    redeem_code_types = {
        "silver_guild_preminum": "Silver Guild Premium",
        "golden_guild_premium": "Golden Guild Premium",
        "diamond_guild_premium": "Diamond Guild Premium",
        "user_no_prefix": "User No Prefix"
    }


class database():
    host = os.getenv("DB_HOST")
    port = int(os.getenv("DB_PORT")) if os.getenv("DB_PORT") else 5432
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    name = os.getenv("DB_NAME")