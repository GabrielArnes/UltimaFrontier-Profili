import discord
from discord import app_commands
import random
import json
import os
from dotenv import load_dotenv
import discord
from discord import app_commands,Embed, app_commands, Interaction
import os
import json
from discord.ui import View, Select, Button
import misc_commands
import pg_commands


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True  # Necessario per accedere ai membri in voice chat

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = MyClient()


misc_commands.setup_commands(client)
pg_commands.setup_commands(client)


# PROFILI V0.1

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

client.run(TOKEN)
