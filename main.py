"""Main program for the bot.

This file inherits from all command files and runs the bot.
"""

from setup import *
from viewstats import *


@client.event
async def on_ready():
    print(f"{client.user} is ready!")
    await client.change_presence(
        status=Status.online, activity=Activity(type=ActivityType.watching, name="you")
    )
    await tree.sync()


@client.event
async def on_message(message: Message):
    if (message.author.id in COLLABORATORS or not BLOCK_COMMANDS) and \
            isinstance(message.channel, DMChannel):
        # This assumes character has already been created, or else user does not have permission
        # TODO: change logic for jury, also do not listen until the game has started
        print(message.content)
        encrypted_user_id = encrypt_id(message.author.id)
        character = characters_db.find_one({"_id": encrypted_user_id})
        character_name, current_room = character["character_name"], character["current_room"]
        channel_id = CHANNEL_IDS[current_room]
        channel = client.get_channel(channel_id)
        await channel.send(f"**{character_name}**: {message.content}")


@tree.command(name="ping", description="Pings the bot")
async def ping(interaction: Interaction):
    if interaction.user.id in COLLABORATORS or not BLOCK_COMMANDS:
        await interaction.response.send_message("Pong!")
    else:
        await interaction.response.send_message(embed=no_permission_embed, ephemeral=True)


@tree.command(name="setup", description="Initialize a character")
async def setup(interaction: Interaction):
    if interaction.user.id in COLLABORATORS or not BLOCK_COMMANDS:
        await interaction.response.send_message(embed=confirm_command_embed, ephemeral=True)
        user_id = interaction.user.id
        encrypted_user_id = encrypt_id(user_id)
        character = characters_db.find_one({"_id": encrypted_user_id})
        if character is None:
            view = KeynoteConfirmView(interaction)
            await interaction.user.send(embed=keynote_embed, view=view)
        else:
            view = InitialDuplicateStartOverView(interaction)
            await interaction.user.send(embed=already_has_character_embed, view=view)
    else:
        await interaction.response.send_message(embed=no_permission_embed, ephemeral=True)


# @tree.command(name="viewstats", description="View all characters' stats")
# async def viewstats(interaction: Interaction):
#     if interaction.user.id in COLLABORATORS or not BLOCK_COMMANDS:
#         ...
#     else:
#         await interaction.response.send_message(embed=no_permission_embed, ephemeral=True)


if __name__ == "__main__":
    print(characters_db)
    client.run(token)
