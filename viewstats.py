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
        self.thumbnail_file, self.embed = None, None
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
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='◀️', style=ButtonStyle.blurple, custom_id='previous')
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the previous page.

        Args:
            interaction (discord.Interaction): The interaction that triggered this button.
            button (discord.ui.Button): The button that was clicked.
        """
        self.page -= 1
        await self.update_interaction(interaction)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='▶️', style=ButtonStyle.blurple, custom_id='next')
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the next page.

        Args:
            interaction (discord.Interaction): The interaction that triggered this button.
            button (discord.ui.Button): The button that was clicked.
        """
        self.page += 1
        await self.update_interaction(interaction)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='⏭️', style=ButtonStyle.green, custom_id='last')
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the last page.

        Args:
            interaction (discord.Interaction): The interaction that triggered this button.
            button (discord.ui.Button): The button that was clicked.
        """
        self.page = self.max_page
        await self.update_interaction(interaction)
        await interaction.response.edit_message(view=self)

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
        self.update_interaction(interaction)

    async def update_interaction(self, interaction: discord.Interaction) -> None:
        # TODO: may not need to update them all when the characters list is set in stone after testing
        self.characters = [document for document in characters_db.find()]
        self.current_character = self.characters[self.page]
        self.max_page = len(self.characters) - 1
        self.update_buttons()
        self.thumbnail_file = get_thumbnail_file(self.current_character["portrait_emoji_pair"])
        # TODO: come up with more
