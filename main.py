"""Main program for the bot."""

from setup import *


@client.event
async def on_ready():
    print(f"{client.user} is ready!")
    await client.change_presence(
        status=Status.online, activity=Activity(type=ActivityType.watching, name="you")
    )
    await tree.sync()


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


if __name__ == "__main__":
    print(characters_db)
    client.run(token)
