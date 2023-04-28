"""Configuration file for discord api and other token related stuffs.

Also includes general embeds used across multiple commands.
"""

import os

import certifi
import pymongo
import discord.ui
from discord import *
from dotenv import load_dotenv

intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)

tree = app_commands.CommandTree(client)

load_dotenv()
token = os.getenv("token")
connection_string = os.getenv("connection")
mongo_client = pymongo.MongoClient(connection_string, tlsCAFile=certifi.where())
characters_db = mongo_client["OI-Big-Brother"]["characters"]

COLLABORATORS = [
    214607100582559745,
    277621798357696513,
    660721501791715329,
    176461616546709504,
    690534844710649856,
    497886145858764801,
    233678479458172930
]

BLOCK_COMMANDS = True

# Embed to show when user attempts to use a command they don't have permission to use
no_permission_embed = Embed(
    description="You do not have permission to do this.",
    color=0xFF0000,
)
