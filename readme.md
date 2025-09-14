# Soward Bot Setup Guide

## Prerequisites

Before setting up the bot, ensure you have the following installed:

- Python 3.12 or higher
- pip (Python package installer)
- PostgreSQL (for database)

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/adnanbinpulok/soward-bot.git
   cd soward-bot
   ```

2. **Install the required Python packages:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Set up the environment variables:**

   Create a `.env` file in the

secrets

directory with the following content:

```env
TOKEN = "BOT_TOKEN"
PREFIX = "?"
SHARD_COUNT = 5
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_NAME = "postgres"
```

## Running the Bot

1. **Start the bot:**

   ```sh
   python main.py
   ```

2. **Verify the bot is running:**

   Check the bot's status in your Discord server. It should be online and responsive to commands.

## Additional Configuration

### Setting Up Modules

You can set up various modules using the bot's commands. Here are some examples:

- **AutoMod Module:**

  ```sh
  !setup automod
  ```

- **AntiNuke Module:**

  ```sh
  !setup antinuke
  ```

- **Logging Module:**

  ```sh
  !setup logging
  ```

- **Ticket System Module:**

  ```sh
  !setup ticket
  ```

- **Welcomer Module:**

  ```sh
  !setup welcomer
  ```

- **Music Module:**

  ```sh
  !setup music
  ```

## Support

For support, join our [Discord server](https://discord.gg/Wn5apddvpa) or contact us via [email](mailto:adnanbinpulok@gmail.com).

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

Thank you for using Soward Bot!
