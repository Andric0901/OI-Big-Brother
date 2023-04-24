"""OI Big Brother Bot"""

import os
from elements import *
import certifi
from dotenv import load_dotenv
import pymongo

load_dotenv()
token = os.getenv("token")
connection_string = os.getenv("connection")
mongo_client = pymongo.MongoClient(connection_string, tlsCAFile=certifi.where())
characters_db = mongo_client["OI-Big-Brother"]["characters"]


@client.event
async def on_ready():
    print(f"{client.user} is ready!")
    await client.change_presence(
        status=Status.online, activity=Activity(type=ActivityType.watching, name="you")
    )
    await tree.sync()


@tree.command(name="ping", description="Pings the bot")
async def ping(interaction: Interaction):
    await interaction.response.send_message("Pong!")


@tree.command(name="setup", description="Initialize a character")
async def setup(interaction: Interaction):
    await interaction.response.send_message(embed=confirm_command_embed, ephemeral=True)
    view = KeynoteConfirmView(interaction)
    await interaction.user.send(embed=keynote_embed, view=view)


if __name__ == "__main__":
    print(characters_db)
    client.run(token)
