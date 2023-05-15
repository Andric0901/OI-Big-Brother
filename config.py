"""Configuration file for discord api and other token related stuffs.

Also includes general embeds and functions used across multiple commands.

This is a parent file to all command files, which is then inherited to main.py.
"""

import os
from pathlib import Path
from typing import Union, Optional

from abc import ABCMeta, abstractmethod
import certifi
import discord.ui
import pymongo
from discord import *
from dotenv import load_dotenv

# Set up client and intents for the discord bot
intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)

# Set up command tree for slash commands
tree = app_commands.CommandTree(client)

# Set up environment variables
load_dotenv()
token = os.getenv("token")
connection_string = os.getenv("connection")
encryption_key = os.getenv("encryption_key")
mongo_client = pymongo.MongoClient(connection_string, tlsCAFile=certifi.where())
characters_db = mongo_client["OI-Big-Brother"]["characters"]

COLLABORATORS = [
    214607100582559745,
    277621798357696513,
    660721501791715329,
    176461616546709504,
    690534844710649856,
    497886145858764801,
    233678479458172930,
    918012501747183628
]

CHANNEL_IDS = {
    "bb-announcements": 1102570924223512619,
    "view-stats": 1102571016531759195,
    "jury-chat": 1102570847014752368,
    "HoH Bedroom": 1102571134312009829,
    "Bedroom 1": 1102571195490115594,
    "Bedroom 2": 1102571228302164112,
    "Lounge": 1102571294186295306,
    "Kitchen": 1102571326251741184,
    "Backyard": 1102571366189891614
}

BLOCK_COMMANDS = True

# Embed to show when user attempts to use a command they don't have permission to use
no_permission_embed = Embed(
    description="You do not have permission to do this.",
    color=0xFF0000,
)


def encrypt_id(unencrypted_id: Union[int, str]) -> str:
    """Encrypts the discord user id using the encryption key.

    Args:
        unencrypted_id (Union[int, str]): The discord user id to encrypt.

    Returns:
        str: The encrypted discord user id.
    """
    return str(int(unencrypted_id) + int(encryption_key))


def decrypt_id(encrypted_id: Union[int, str]) -> str:
    """Decrypts the discord user id using the encryption key.

    Args:
        encrypted_id (Union[int, str]): The discord user id to decrypt.

    Returns:
        str: The decrypted discord user id.
    """
    return str(int(encrypted_id) - int(encryption_key))


def get_thumbnail_file(portrait_number: int) -> discord.File:
    """Return the thumbnail file used for each character.

    Args:
        portrait_number: (int) portrait number for the character.

    Returns:
        discord.File: A discord file "image.jpg" with the thumbnail.
    """
    thumbnail_path = Path(__file__).parent / f"assets/{portrait_number}.jpg"
    thumbnail_file = discord.File(thumbnail_path, 'image.jpg')
    return thumbnail_file
