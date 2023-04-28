"""Elements for the /setup command, including embeds and views."""

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
    def __init__(self, interaction: Interaction):
        super().__init__()
        self.interaction = interaction

    @discord.ui.button(label="Start Over", style=ButtonStyle.blurple)
    async def start_over(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        user_id = self.interaction.user.id
        encrypted_user_id = encrypt_id(user_id)
        characters_db.delete_one({"_id": encrypted_user_id})
        assert characters_db.find_one({"_id": encrypted_user_id}) is None
        view = KeynoteConfirmView(self.interaction)
        await self.interaction.user.send(embed=keynote_embed, view=view)

    @discord.ui.button(label="Cancel", style=ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
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

# Third embed of /setup inside DM channel
portrait_emoji_select_embed = Embed(
    title="Welcome, player!",
    description="Select from this list of available portraits and emojis: (Google Docs Link)\n"
                "\n**Already chosen by other players:** (...)",
    color=0x00FF00,
)

# Select options for View with portrait_emoji_select_embed
# To avoid confusion, value will be set equal to label
# TODO: remember to use i - 1 for indexing purposes
portrait_emoji_select_options = [SelectOption(label=f"{i}") for i in range(1, 26)]

# Fourth embed of /setup inside DM channel
starting_room_select_embed = Embed(
    title="Choose a starting room",
    description="Select from this list of available rooms: (...)\n",
    color=0x00FF00,
)

# Select options for View with starting_room_select_embed
# To avoid confusion, value will be set equal to label (without "Room ")
# TODO: remember to use i - 1 for indexing purposes
starting_room_select_options = [SelectOption(label=f"Room {i}", value=f"{i}")
                                for i in range(1, 16)]

# List of stats that the user will be able to choose from
STATS_OPTIONS = [
    "Hunger Level", "Activity Level", "Energy Level", "Strength",
    "Agility", "Intelligence", "Creativity"
]

# Fifth embed of /setup inside DM channel (edited over recursive calls)
# TODO: Could also give a short description of each stat
# If change in STATS_OPTIONS, this needs to be modified manually
starting_stats_select_embed = Embed(
    title="Choose starting stats",
    description="You have 20 points to distribute among the following stats:\n"
                "\n**Hunger Level**: 0"
                "\n**Activity Level**: 0"
                "\n**Energy Level**: 0"
                "\n**Strength**: 0"
                "\n**Agility**: 0"
                "\n**Intelligence**: 0"
                "\n**Creativity**: 0"
                "\n\nSelect number of points for your **Hunger Level**:",
    color=0x00FF00,
)

# Select options for View with starting_stats_select_embed
starting_stats_select_options = [SelectOption(label=f"{i}")
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

# Embed to show when the portrait/emoji is already taken
portrait_emoji_taken_embed = Embed(
    title="Portrait/Emoji already taken!",
    description="Someone (out of all odds) chose the same portrait/emoji pair before you...\n"
                "Please start over by clicking the button below.",
    color=0xFF0000,
)

########################################
# Views for /setup command
# Order of views:
# KeynoteConfirmView -> PortraitEmojiSelectView ->
# StartingRoomSelectView -> StartingStatsSelectView -> FinalSetupConfirmationView
########################################


class KeynoteConfirmView(discord.ui.View):
    def __init__(self, interaction: Interaction):
        super().__init__()
        self.interaction = interaction
        self.character_name = None

    @discord.ui.button(label="I understand", style=ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.remove_item(button)
        await interaction.response.edit_message(embed=character_name_request_embed, view=None)

        def check(m):
            return m.author == interaction.user and isinstance(m.channel, DMChannel)

        msg = await client.wait_for("message", check=check)
        self.character_name = msg.content
        await interaction.message.delete()
        portrait_emoji_select_embed.title = f"Welcome, {self.character_name}!"
        chosen_portrait_emoji_pairs = updated_db_elements()[1]
        updated_string = "" + ", ".join(chosen_portrait_emoji_pairs) + ""
        portrait_emoji_select_embed.description = portrait_emoji_select_embed.description.\
            replace("(...)", updated_string)
        view = PortraitEmojiSelectView(interaction)
        view.character_name = self.character_name
        view.children[0].options = [element for element in portrait_emoji_select_options
                                    if element.label not in chosen_portrait_emoji_pairs]
        await interaction.followup.send(embed=portrait_emoji_select_embed, view=view)


class PortraitEmojiSelectView(KeynoteConfirmView):
    def __init__(self, interaction: Interaction):
        super().__init__(interaction)
        # This indicator is a STRING
        self.portrait_emoji_pair = None
        self.options = portrait_emoji_select_options.copy()
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                self.remove_item(child)

    @discord.ui.select(placeholder="Select a pair...",
                       options=portrait_emoji_select_options)
    async def select(self, interaction: Interaction, select: discord.ui.Select):
        self.portrait_emoji_pair = select.values[0]
        view = StartingRoomSelectView(interaction)
        view.character_name = self.character_name
        view.portrait_emoji_pair = self.portrait_emoji_pair
        await interaction.response.edit_message(embed=starting_room_select_embed,
                                                view=view)


class StartingRoomSelectView(PortraitEmojiSelectView):
    def __init__(self, interaction: Interaction):
        super().__init__(interaction)
        self.starting_room = None
        self.options = starting_room_select_options
        self.children.clear()

    @discord.ui.select(placeholder="Select a starting room...",
                       options=starting_room_select_options)
    async def select(self, interaction: Interaction, select: discord.ui.Select):
        self.starting_room = select.values[0]
        view = StartingStatsSelectView(interaction)
        view.character_name = self.character_name
        view.portrait_emoji_pair = self.portrait_emoji_pair
        view.starting_room = self.starting_room
        await interaction.response.edit_message(embed=starting_stats_select_embed,
                                                view=view)


class StartingStatsSelectView(StartingRoomSelectView):
    def __init__(self, interaction: Interaction):
        super().__init__(interaction)
        self.current_stat = "Hunger Level"
        self.max_points = 20
        self.starting_stats = {stat: 0 for stat in STATS_OPTIONS}
        # Future recursive calls to this class will modify these
        # two instance variables, use copy to prevent mutation
        self.options = starting_stats_select_options.copy()
        self.embed = starting_stats_select_embed.copy()
        for child in self.children:
            if child.custom_id != "starting_stats_select":
                self.remove_item(child)

    @discord.ui.select(placeholder="Points for Hunger Level...",
                       options=starting_stats_select_options,
                       custom_id="starting_stats_select")
    async def select(self, interaction: Interaction, select: discord.ui.Select):
        point_given = int(select.values[0])
        self.starting_stats[self.current_stat] = int(select.values[0])
        self.max_points -= point_given
        if self.current_stat == STATS_OPTIONS[-2] or self.max_points == 0:
            if self.current_stat == STATS_OPTIONS[-2]:
                self.starting_stats[STATS_OPTIONS[-1]] = self.max_points
            embed = final_setup_confirmation_embed.copy()
            embed.add_field(name="Character Name", value=self.character_name, inline=True)
            embed.add_field(name="Portrait Emoji Pair", value=f"{str(int(self.portrait_emoji_pair))}",
                                 inline=True)
            embed.add_field(name="Starting Room", value=f"Room {str((int(self.starting_room)))}", inline=True)
            embed.add_field(name="Starting Stats",
                                 value="\n".join(
                                     [f"**{stat}**: {value}" for stat, value in self.starting_stats.items()]),
                                 inline=False)
            view = FinalSetupConfirmationView(interaction, self.character_name, self.portrait_emoji_pair,
                                              self.starting_room, self.starting_stats, embed)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            self.options = [SelectOption(label=f"{i}") for i in range(0, self.max_points + 1)]
            self.current_stat = STATS_OPTIONS[STATS_OPTIONS.index(self.current_stat) + 1]
            self.embed.description = f"You have {self.max_points} points to distribute among the following stats:\n" \
                                     f"\n**Hunger Level**: {self.starting_stats['Hunger Level']}" \
                                     f"\n**Activity Level**: {self.starting_stats['Activity Level']}" \
                                     f"\n**Energy Level**: {self.starting_stats['Energy Level']}" \
                                     f"\n**Strength**: {self.starting_stats['Strength']}" \
                                     f"\n**Agility**: {self.starting_stats['Agility']}" \
                                     f"\n**Intelligence**: {self.starting_stats['Intelligence']}" \
                                     f"\n**Creativity**: {self.starting_stats['Creativity']}" \
                                     f"\n\nSelect number of points for your **{self.current_stat}**:"
            new_view = StartingStatsSelectView(interaction)
            new_view.starting_stats = self.starting_stats
            new_view.max_points = self.max_points
            new_view.current_stat = self.current_stat
            new_view.options = self.options
            new_view.embed = self.embed
            new_view.character_name = self.character_name
            new_view.portrait_emoji_pair = self.portrait_emoji_pair
            new_view.starting_room = self.starting_room
            new_view.children[0].placeholder = f"Points for {self.current_stat}..."
            new_view.children[0].options = self.options
            await interaction.response.edit_message(embed=self.embed, view=new_view)


class FinalSetupConfirmationView(discord.ui.View):
    def __init__(self, interaction: Interaction, character_name: str, portrait_emoji_pair: str,
                 starting_room: str, starting_stats: dict, embed: Embed):
        super().__init__()
        self.interaction = interaction
        self.character_name = character_name
        self.portrait_emoji_pair = portrait_emoji_pair
        self.starting_room = starting_room
        self.starting_stats = starting_stats
        self.embed = embed

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        chosen_character_names, chosen_portrait_emoji_pairs = updated_db_elements()
        if self.character_name in chosen_character_names:
            await interaction.message.delete()
            await interaction.followup.send(embed=self.embed)
            view = ConfirmDuplicateStartOverView(interaction)
            await interaction.followup.send(embed=character_name_taken_embed, view=view)
        elif self.portrait_emoji_pair in chosen_portrait_emoji_pairs:
            await interaction.message.delete()
            await interaction.followup.send(embed=self.embed)
            view = ConfirmDuplicateStartOverView(interaction)
            await interaction.followup.send(embed=portrait_emoji_taken_embed, view=view)
        else:
            user_id = str(interaction.user.id)
            encrypted_user_id = encrypt_id(user_id)
            data = {
                "character_name": self.character_name,
                "portrait_emoji_pair": self.portrait_emoji_pair,
                "starting_room": self.starting_room,
                "starting_stats": self.starting_stats
            }
            characters_db.update_one({"_id": encrypted_user_id}, {"$set": data}, upsert=True)
            await interaction.followup.send("Character Saved!", embed=self.embed)
            await interaction.message.delete()
            # chosen_character_names, chosen_portrait_emoji_pairs = updated_db_elements()
            # print(chosen_character_names, chosen_portrait_emoji_pairs)

    @discord.ui.button(label="Start Over", style=discord.ButtonStyle.red)
    async def start_over(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message(embed=self.embed)
        user_id = str(interaction.user.id)
        encrypted_user_id = encrypt_id(user_id)
        characters_db.delete_one({"_id": encrypted_user_id})
        view = KeynoteConfirmView(interaction)
        await interaction.user.send(embed=keynote_embed, view=view)


class ConfirmDuplicateStartOverView(discord.ui.View):
    def __init__(self, interaction: Interaction):
        super().__init__()
        self.interaction = interaction

    @discord.ui.button(label="Start Over", style=discord.ButtonStyle.red)
    async def start_over(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        user_id = str(interaction.user.id)
        encrypted_user_id = encrypt_id(user_id)
        characters_db.delete_one({"_id": encrypted_user_id})
        view = KeynoteConfirmView(interaction)
        await interaction.user.send(embed=keynote_embed, view=view)


def updated_db_elements() -> tuple[list, list]:
    """Return updated chosen_character_names and
    chosen_portrait_emoji_pairs from the database."""
    chosen_character_names = []
    chosen_portrait_emoji_pairs = []
    for document in characters_db.find():
        chosen_character_names.append(document["character_name"])
        chosen_portrait_emoji_pairs.append(document["portrait_emoji_pair"])
    return chosen_character_names, chosen_portrait_emoji_pairs
