"""OI Big Brother Bot"""

import os

import certifi
from dotenv import load_dotenv
import discord
import pymongo
from discord import Activity, ActivityType, Status, app_commands, Intents

load_dotenv()
token = os.getenv("token")
connection_string = os.getenv("connection")
mongo_client = pymongo.MongoClient(connection_string, tlsCAFile=certifi.where())
characters_db = mongo_client["OI-Big-Brother"]["characters"]

intents = Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print(f"{client.user} is ready!")
    await client.change_presence(
        status=Status.online, activity=Activity(type=ActivityType.watching, name="you")
    )
    await tree.sync()


@tree.command(name="ping", description="Pings the bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")


@tree.command(name="setup", description="Initialize a character")
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message("Setup!")

if __name__ == "__main__":
    print(characters_db)
    client.run(token)
