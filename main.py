import discord
import os
import sys
from dotenv import load_dotenv
from discord import app_commands, app_commands
import misc_commands
import pg_commands
from utils import extra_bersagli


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
    
    async def on_disconnect(self):
        print("Errore, termino il processo...")
        sys.exit(1)

client = MyClient()


misc_commands.setup_commands(client)
pg_commands.setup_commands(client)

@client.event
async def on_voice_state_update(member, before, after):
    # Se l'utente lascia del tutto la vocale, resetta i bersagli extra
    if before.channel is not None and after.channel is None:
        user_id = member.id
        if user_id in extra_bersagli:
            del extra_bersagli[user_id]


# PROFILI V0.1

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

client.run(TOKEN)
