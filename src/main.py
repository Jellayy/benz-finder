import interactions
from interactions import slash_command, SlashContext
import os


client = interactions.Client()


@interactions.listen()
async def on_startup():
    print('Logged in!')


client.load_extension('extensions.commands')

client.start(os.environ['DISCORD_BOT_TOKEN'])
