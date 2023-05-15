"""Elements for the /setup command, including embeds and views."""
import discord

from config import *

########################################
# Elements for /setup command
########################################

# Embed to show when user (who has permission to do so) uses the /setup command
confirm_command_embed = Embed(
    description="I've sent you a DM!",
    color=0x00FF00,
)

# Embed to show when user attempts to create another character
already_has_character_embed = Embed(
    title="You already have made a character!",
    description="If you want to change your character, click the 'Start Over' button below.\n"
                "Note: This will delete your current character.",
    color=0xFF0000,
)


class InitialDuplicateStartOverView(discord.ui.View):
    """A View to show when user attempts to create another character."""

    def __init__(self, interaction: Interaction):
        super().__init__()
        self.interaction = interaction

    @discord.ui.button(label="Start Over", style=ButtonStyle.blurple)
    async def start_over(self, interaction: discord.Interaction, button: discord.ui.Button):
        """A button to start the character creation process again.

        Args:
            interaction (discord.Interaction): The interaction that triggered this View.
            button (discord.ui.Button): The button that triggered this function.
        """
        await interaction.message.delete()
        user_id = self.interaction.user.id
        encrypted_user_id = encrypt_id(user_id)
        characters_db.delete_one({"_id": encrypted_user_id})
        assert characters_db.find_one({"_id": encrypted_user_id}) is None
        view = KeynoteConfirmView(self.interaction)
        await self.interaction.user.send(embed=keynote_embed, view=view)

    @discord.ui.button(label="Cancel", style=ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """A button to cancel the character creation process."""
        await interaction.message.delete()


# First embed of /setup inside DM channel
keynote_embed = Embed(
    title="Before we start...",
    description="**Here are some things to keep in mind:**\n"
                "\n✅ You can only have one character at a time."
                "\n✅ Think of a creative name for your character!"
                "\n✅ Each character will get its own portrait and representative emoji."
                "\n✅ You can change your character's details at any time, until the game starts."
                "\n✅ At the end, you will have a chance to review the details, and start over if needed."
                "\n✅ Your character will be anonymized, even to the jurors and developers."
                "\n✅ We recommend completing the creation within 10 minutes to avoid duplicates.",
    color=0x00FF00,
)

# Second embed of /setup inside DM channel
character_name_request_embed = Embed(
    title="What is the name of the character?",
    description="Choose a creative name!",
    color=0x00FF00,
)

# Fourth embed of /setup inside DM channel
starting_room_select_embed = Embed(
    title="Welcome, player!",
    description="Select your starting room from this list of available rooms: \n"
                "\n- Bedroom 1"
                "\n- Bedroom 2"
                "\n- Lounge"
                "\n- Kitchen"
                "\n- Backyard",
    color=0x00FF00,
)

# Select options for View with starting_room_select_embed
# Values after select will be set equal to label
starting_room_select_options = [SelectOption(label="Bedroom 1"),
                                SelectOption(label="Bedroom 2"),
                                SelectOption(label="Lounge"),
                                SelectOption(label="Kitchen"),
                                SelectOption(label="Backyard")]

# List of stats that the user will be able to choose from
TRAITS_OPTIONS = ["Strength", "Dexterity", "Constitution", "Intelligence", "Charisma"]

# Fifth embed of /setup inside DM channel (edited over recursive calls)
# TODO: Could also give a short description of each stat
# If change in TRAITS_OPTIONS, this needs to be modified manually
starting_traits_select_embed = Embed(
    title="Distribute points for starting traits",
    description="You have 60 points to distribute among the following traits, with\n"
                "**20 points maximum** for each trait:\n"
                "\n**Strength**: 0"
                "\n**Dexterity**: 0"
                "\n**Constitution**: 0"
                "\n**Intelligence**: 0"
                "\n**Charisma**: 0"
                "\n\nSelect number of points for your **Strength**:",
    color=0x00FF00,
)

# Select options for View with starting_traits_select_embed
starting_traits_select_options = [SelectOption(label=f"{i}")
                                  for i in range(0, 21)]

# Sixth embed of /setup inside DM channel
final_setup_confirmation_embed = Embed(
    title="Character Details",
    color=0x00FF00,
)

# Embed to show when the character name is already taken
character_name_taken_embed = Embed(
    title="Character name already taken!",
    description="Someone (out of all odds) chose the same name before you...\n"
                "Please start over by clicking the button below.",
    color=0xFF0000,
)


class KeynoteConfirmView(discord.ui.View):
    """A View to confirm that the user has read the keynote."""

    def __init__(self, interaction: Interaction):
        super().__init__()
        self.interaction = interaction
        self.character_name = None

    @discord.ui.button(label="I understand", style=ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        """A button to confirm that the user has read the keynote."""
        self.remove_item(button)
        await interaction.response.edit_message(embed=character_name_request_embed, view=None)

        def check(m) -> bool:
            """Check that the message is sent by the user in DMs."""
            return m.author == interaction.user and isinstance(m.channel, DMChannel)

        msg = await client.wait_for("message", check=check)
        self.character_name = msg.content
        await interaction.message.delete()

        starting_room_select_embed.title = f"Welcome, {self.character_name}!"
        view = StartingRoomSelectView(interaction)
        view.character_name = self.character_name
        for child in view.children:
            if child.custom_id != "starting_room_select":
                view.remove_item(child)
        await interaction.followup.send(embed=starting_room_select_embed, view=view)


class StartingRoomSelectView(KeynoteConfirmView):
    """A View to select a starting room."""

    def __init__(self, interaction: Interaction):
        super().__init__(interaction)
        self.starting_room = None
        self.options = starting_room_select_options
        self.children.clear()

    @discord.ui.select(placeholder="Select a starting room...",
                       options=starting_room_select_options,
                       custom_id="starting_room_select")
    async def select(self, interaction: Interaction, select: discord.ui.Select):
        """A select menu to select a starting room.

        Args:
            interaction (Interaction): The interaction that triggered this View.
            select (discord.ui.Select): The select menu that triggered this function.
        """
        self.starting_room = select.values[0]
        view = StartingTraitsSelectView(interaction)
        view.character_name = self.character_name
        view.starting_room = self.starting_room
        await interaction.response.edit_message(embed=starting_traits_select_embed,
                                                view=view)


class StartingTraitsSelectView(StartingRoomSelectView):
    """A View to distribute points for starting traits."""

    def __init__(self, interaction: Interaction):
        super().__init__(interaction)
        self.current_trait = 0
        self.max_points = 20
        self.min_points = 0
        self.points_so_far = 0
        self.options = starting_traits_select_options.copy()
        self.embed = starting_traits_select_embed.copy()
        self.starting_traits = {trait: 0 for trait in TRAITS_OPTIONS}
        for child in self.children:
            if child.custom_id != "starting_traits_select":
                self.remove_item(child)

    @discord.ui.select(placeholder="Points for Strength...",
                       options=starting_traits_select_options,
                       custom_id="starting_traits_select")
    async def select(self, interaction: Interaction, select: discord.ui.Select):
        points_given = int(select.values[0])
        self.points_so_far += points_given
        self.starting_traits[TRAITS_OPTIONS[self.current_trait]] = points_given
        self.current_trait += 1
        self.min_points = new_min_points(current_trait=self.current_trait,
                                         points_so_far=self.points_so_far)
        self.max_points = new_max_points(current_trait=self.current_trait,
                                         points_so_far=self.points_so_far)
        if self.current_trait == 4 or self.min_points == 20 or self.max_points == 0:
            if self.current_trait == 4:
                assert 0 <= 60 - self.points_so_far <= 20
                self.starting_traits[TRAITS_OPTIONS[self.current_trait]] = 60 - self.points_so_far
            elif self.min_points == 20:
                for i in range(self.current_trait, 5):
                    self.starting_traits[TRAITS_OPTIONS[i]] = 20
            elif self.max_points == 0:
                for i in range(self.current_trait, 5):
                    self.starting_traits[TRAITS_OPTIONS[i]] = 0
            embed = final_setup_confirmation_embed.copy()
            embed.add_field(name="Character Name", value=self.character_name, inline=True)
            embed.add_field(name="Starting Room", value=self.starting_room, inline=True)
            embed.add_field(name="Starting Traits", value="\n".join([f"{trait}: {points}" for trait, points
                                                                     in self.starting_traits.items()]), inline=False)
            view = FinalSetupConfirmationView(interaction, self.character_name, self.starting_room,
                                              self.starting_traits, embed)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            self.options = [SelectOption(label=f"{i}") for i in range(self.min_points, self.max_points + 1)]
            self.embed.description = f"You have **{60 - self.points_so_far} points left** to distribute, with\n" \
                                     "**20 points maximum** for each trait:\n" \
                                     f"\n**Strength**: {self.starting_traits['Strength']}" \
                                     f"\n**Dexterity**: {self.starting_traits['Dexterity']}" \
                                     f"\n**Constitution**: {self.starting_traits['Constitution']}" \
                                     f"\n**Intelligence**: {self.starting_traits['Intelligence']}" \
                                     f"\n**Charisma**: {self.starting_traits['Charisma']}" \
                                     f"\n\nSelect number of points for your **{TRAITS_OPTIONS[self.current_trait]}**:"
            new_view = StartingTraitsSelectView(interaction)
            new_view.character_name = self.character_name
            new_view.starting_room = self.starting_room
            new_view.starting_traits = self.starting_traits
            new_view.current_trait = self.current_trait
            new_view.max_points = self.max_points
            new_view.min_points = self.min_points
            new_view.points_so_far = self.points_so_far
            new_view.options = self.options
            new_view.embed = self.embed
            new_view.children[0].placeholder = f"Points for {TRAITS_OPTIONS[self.current_trait]}..."
            new_view.children[0].options = self.options
            await interaction.response.edit_message(embed=self.embed, view=new_view)


class FinalSetupConfirmationView(discord.ui.View):
    """A View to confirm final step of the setup."""

    def __init__(self, interaction: Interaction, character_name: str,
                 starting_room: str, starting_traits: dict, embed: Embed):
        super().__init__()
        self.interaction = interaction
        self.character_name = character_name
        self.starting_room = starting_room
        self.starting_traits = starting_traits
        # portrait_emoji_pair is an integer, starting 0
        self.portrait_emoji_pair = None
        self.embed = embed

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: Interaction, button: discord.ui.Button):
        """A button to confirm final step of the setup.

        Args:
            interaction (Interaction): The interaction that triggered this View.
            button (discord.ui.Button): The button that triggered this function.
        """
        await interaction.response.defer()
        chosen_character_names = updated_db_elements()[0]
        self.portrait_emoji_pair = assign_portrait_emoji_pair()
        if self.character_name in chosen_character_names:
            await interaction.message.delete()
            await interaction.followup.send(embed=self.embed)
            view = ConfirmDuplicateStartOverView(interaction)
            await interaction.followup.send(embed=character_name_taken_embed, view=view)
        else:
            user_id = str(interaction.user.id)
            encrypted_user_id = encrypt_id(user_id)
            data = {
                "character_name": self.character_name,
                "portrait_emoji_pair": self.portrait_emoji_pair,
                "starting_room": self.starting_room,
                "status": "in house",
                "traits": self.starting_traits,
                "stats": {  # TODO: max 100? 200?
                    "Hunger": 100,
                    "Energy": 100,
                    "Activity": 100,
                    "Socialization": 100
                },
                # TODO: implement relationship stats (standard distribution, how exactly?)
            }
            characters_db.update_one({"_id": encrypted_user_id}, {"$set": data}, upsert=True)
            # Get the thumbnail file, set it as thumbnail for the embed, and upload the
            # file itself as well when sending followup
            thumbnail_file = get_thumbnail_file(self.portrait_emoji_pair)
            self.embed.set_thumbnail(url='attachment://image.jpg')
            await interaction.followup.send("Character Saved!", embed=self.embed, files=[thumbnail_file])
            await interaction.message.delete()

    @discord.ui.button(label="Start Over", style=discord.ButtonStyle.red)
    async def start_over(self, interaction: Interaction, button: discord.ui.Button):
        """A button to start over the setup.

        Args:
            interaction (Interaction): The interaction that triggered this View.
            button (discord.ui.Button): The button that triggered this function.
        """
        await interaction.message.delete()
        await interaction.response.send_message(embed=self.embed)
        user_id = str(interaction.user.id)
        encrypted_user_id = encrypt_id(user_id)
        characters_db.delete_one({"_id": encrypted_user_id})
        view = KeynoteConfirmView(interaction)
        await interaction.user.send(embed=keynote_embed, view=view)


class ConfirmDuplicateStartOverView(discord.ui.View):
    """A View to confirm starting over the setup after
    a duplicate character name or portrait emoji pair."""

    def __init__(self, interaction: Interaction):
        super().__init__()
        self.interaction = interaction

    @discord.ui.button(label="Start Over", style=discord.ButtonStyle.red)
    async def start_over(self, interaction: Interaction, button: discord.ui.Button):
        """A button to start over the setup.

        Args:
            interaction (Interaction): The interaction that triggered this View.
            button (discord.ui.Button): The button that triggered this function.
        """
        await interaction.message.delete()
        user_id = str(interaction.user.id)
        encrypted_user_id = encrypt_id(user_id)
        characters_db.delete_one({"_id": encrypted_user_id})
        view = KeynoteConfirmView(interaction)
        await interaction.user.send(embed=keynote_embed, view=view)


def updated_db_elements() -> tuple[list, list]:
    """Return updated chosen_character_names and
    chosen_portrait_emoji_pairs from the database.

    Returns:
        tuple[list, list]: Updated chosen_character_names and
        chosen_portrait_emoji_pairs from the database.
    """
    chosen_character_names = []
    chosen_portrait_emoji_pairs = []
    for document in characters_db.find():
        chosen_character_names.append(document["character_name"])
        chosen_portrait_emoji_pairs.append(document["portrait_emoji_pair"])
    return chosen_character_names, chosen_portrait_emoji_pairs


def assign_portrait_emoji_pair() -> int:
    """Return the appropriate portrait emoji pair given the chosen pairs in the db."""
    chosen_portrait_emoji_pairs = set(updated_db_elements()[1])
    if len(chosen_portrait_emoji_pairs) == 0:
        return 0
    else:
        max_elem = max(chosen_portrait_emoji_pairs)
        default = {i for i in range(max_elem + 1)}
        if default == chosen_portrait_emoji_pairs:
            return max_elem + 1
        else:
            diff = list(default - chosen_portrait_emoji_pairs)
            return min(diff)


def new_max_points(current_trait: int, points_so_far: int) -> int:
    """Return the new maximum points for the select menu in StartingTraitsSelectView."""
    if current_trait <= 2:
        return 20
    else:
        resulting_points = 60 - points_so_far
        if resulting_points >= 20:
            return 20
        else:
            return resulting_points


def new_min_points(current_trait: int, points_so_far: int) -> int:
    """Return the new minimum points for the select menu in StartingTraitsSelectView."""
    if current_trait <= 1:
        return 0
    else:
        len_list = len(TRAITS_OPTIONS)
        assert len_list == 5
        # reserve some points at the end of the list of traits so that
        # if the minimum is picked for the current trait,
        # 20 points are automatically assigned to the rest of the traits
        reserved_points = 20 * (len_list - current_trait - 1)
        resulting_points = 60 - points_so_far - reserved_points
        if resulting_points <= 0:
            return 0
        else:
            return resulting_points
