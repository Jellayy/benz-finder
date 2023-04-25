import interactions
import os
import logging


# Init Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logging.info('MAIN: Logging started!')

# Init Client
client = interactions.Client()


# On Load
@interactions.listen()
async def on_startup():
    print('Logged in!')


# Load Extensions
client.load_extension('extensions.commands')

# Start bot
client.start(os.environ['DISCORD_BOT_TOKEN'])
