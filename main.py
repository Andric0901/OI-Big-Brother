"""OI Big Brothers"""

import os
from dotenv import load_dotenv
import discord
from discord import Activity, ActivityType, Status, app_commands, Intents

load_dotenv()
TOKEN = os.getenv("token")

intents = Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
# For slash commands. Can be changed later
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print(f"{client.user} is ready!")
    await client.change_presence(
        status=Status.online, activity=Activity(type=ActivityType.watching, name="you")
    )
    # For slash commands. Can be changed later
    await tree.sync()


@tree.command(name="ping", description="Pings the bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

if __name__ == "__main__":
    client.run(TOKEN)
