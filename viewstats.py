"""Elements for /viewstats command.

THIS FILE ASSUMES THAT THERE IS AT LEAST ONE CHARACTER IN THE DATABASE.
"""

from config import *


# TODO: PaginationView could be moved to config.py if other files need this class
class PaginationView(discord.ui.View, metaclass=ABCMeta):
    """A parent class for pagination.

    This class implements basic PaginationView to be used in many occasions, including an embed,
    a thumbnail file (if available), and 4 buttons: first, previous, next, last.

    update_interaction is an abstract method to be implemented in the child class.

    Optionally, a child class may implement select() method to add a dropdown menu to the view.
    """

    def __init__(self, current_page: int = 0,
                 timeout: Optional[float] = None,
                 interaction: Optional[discord.Interaction] = None) -> None:
        # TODO: update_interaction must also update self.characters, self.current_character,
        #       and self.max_page
        super().__init__(timeout=timeout)
        assert len([document for document in characters_db.find()]) > 0
        self.characters = [document for document in characters_db.find()]
        self.current_character = self.characters[current_page]
        self.page = current_page
        self.min_page = 0
        self.max_page = len(self.characters) - 1
        self.thumbnail_file = get_thumbnail_file(self.current_character["portrait_emoji_pair"])
        self.embed = create_embed(self.current_character["character_name"],
                                  self.current_character["status"],
                                  self.current_character["current_room"],
                                  self.current_character["stats"],
                                  self.current_character["traits"])
        self.update_buttons()
        self.interaction = interaction

    @discord.ui.button(label='⏮️', style=ButtonStyle.green, custom_id='first')
    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the first page.

        Args:
            interaction (discord.Interaction): The interaction that triggered this button.
            button (discord.ui.Button): The button that was clicked.
        """
        self.page = 0
        await self.update_interaction(interaction)
        try:
            await interaction.response.edit_message(view=self)
        except discord.errors.InteractionResponded:
            pass

    @discord.ui.button(label='◀️', style=ButtonStyle.blurple, custom_id='previous')
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the previous page.

        Args:
            interaction (discord.Interaction): The interaction that triggered this button.
            button (discord.ui.Button): The button that was clicked.
        """
        self.page -= 1
        await self.update_interaction(interaction)
        try:
            await interaction.response.edit_message(view=self)
        except discord.errors.InteractionResponded:
            pass

    @discord.ui.button(label='▶️', style=ButtonStyle.blurple, custom_id='next')
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the next page.

        Args:
            interaction (discord.Interaction): The interaction that triggered this button.
            button (discord.ui.Button): The button that was clicked.
        """
        self.page += 1
        await self.update_interaction(interaction)
        try:
            await interaction.response.edit_message(view=self)
        except discord.errors.InteractionResponded:
            pass

    @discord.ui.button(label='⏭️', style=ButtonStyle.green, custom_id='last')
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the last page.

        Args:
            interaction (discord.Interaction): The interaction that triggered this button.
            button (discord.ui.Button): The button that was clicked.
        """
        self.page = self.max_page
        await self.update_interaction(interaction)
        try:
            await interaction.response.edit_message(view=self)
        except discord.errors.InteractionResponded:
            pass

    @abstractmethod
    async def update_interaction(self, interaction: discord.Interaction):
        """Update the current interaction accordingly.

        This is an abstract method to be implemented in the child class.

        Args:
            interaction (discord.Interaction): The interaction that triggered this button.
        """
        pass

    def update_buttons(self) -> None:
        """Update the buttons accordingly, enabling/disabling them based on the current page."""
        self.children[0].disabled = self.page == 0
        self.children[1].disabled = self.page == 0
        self.children[2].disabled = self.page == self.max_page
        self.children[3].disabled = self.page == self.max_page


class ViewStatsView(PaginationView):
    """The main class for viewing stats for each character, in a dictionary format."""

    def __init__(self, current_page: int = 0,
                 interaction: Optional[Interaction] = None) -> None:
        super().__init__(current_page=current_page)
        self.interaction = interaction

    async def update_interaction(self, interaction: discord.Interaction) -> None:
        # TODO: may not need to update them all when the characters list is set in stone after testing
        self.characters = [document for document in characters_db.find()]
        self.current_character = self.characters[self.page]
        self.max_page = len(self.characters) - 1
        self.update_buttons()
        self.thumbnail_file = get_thumbnail_file(self.current_character["portrait_emoji_pair"])
        self.embed = create_embed(self.current_character["character_name"],
                                  self.current_character["status"],
                                  self.current_character["current_room"],
                                  self.current_character["stats"],
                                  self.current_character["traits"])
        await interaction.response.edit_message(embed=self.embed,
                                                attachments=[self.thumbnail_file],
                                                view=self)


def create_embed(character_name: str,
                 status: str,
                 current_room: str,
                 stats: dict,
                 traits: dict) -> Embed:
    """Create an embed for viewing stats.

    Args:
        character_name (str): The name of the character.
        status (str): The status of the character (in house or jury).
        current_room (str): The current room of the character.
        stats (dict): The stats of the character.
        traits (dict): The traits of the character.
    """
    embed = Embed(title=f"**{character_name}**", color=0x00ff00)
    embed.set_thumbnail(url="attachment://image.jpg")
    embed.add_field(name="Status", value=status, inline=True)
    embed.add_field(name="Current Room", value=current_room, inline=True)
    embed.add_field(name="Stats",
                    value="\n".join([f"{key}: {value}" for key, value in stats.items()]),
                    inline=False)
    embed.add_field(name="Traits",
                    value="\n".join([f"{key}: {value}" for key, value in traits.items()]),
                    inline=False)
    return embed
