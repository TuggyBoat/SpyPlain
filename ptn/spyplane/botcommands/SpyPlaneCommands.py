import discord
from discord import app_commands
from discord.ext import commands

from ptn.spyplane.modules.ErrorHandler import on_app_command_error
from ptn.spyplane.modules.Sheets import values, sheet_dataframe
from ptn.spyplane.modules.SystemScouter import post_scouting


class SpyPlaneCommands(commands.Cog):
    def __init__(self, bot: commands.Cog):
        self.bot = bot

    def cog_load(self):
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = on_app_command_error

    def cog_unload(self):
        tree = self.bot.tree
        tree.on_error = self._old_tree_error

        # Runs scout

    @app_commands.command(name='print_systems')
    async def print_systems(self, interaction: discord.Interaction):
        systems_list = sheet_dataframe['System'].tolist()
        system_string = ''
        for system in systems_list:
            system_string += str(system)+'\n'
        await interaction.response.send_message(system_string)

    @app_commands.command(name='spy_plane_launch')
    async def spy_plane_launch(self, interaction: discord.Interaction):
        await post_scouting(interaction)

