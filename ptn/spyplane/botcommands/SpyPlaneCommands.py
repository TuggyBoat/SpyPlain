import asyncio
import os

import discord
from discord import app_commands
from discord.ext import commands

from ptn.spyplane.database.database import get_all_configs, update_config, find_config, scouting_data_to_csv
from ptn.spyplane.modules.ErrorHandler import on_app_command_error
from ptn.spyplane.modules.Sheets import values, sheet_dataframe, post_list_by_priority
from ptn.spyplane.modules.SystemScouter import post_scouting
import ptn.spyplane.constants as constants


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
        await post_list_by_priority()

    @app_commands.command(name='spy_plane_launch')
    async def spy_plane_launch(self, interaction: discord.Interaction):
        await post_scouting()

    @app_commands.command(name='spy_plane_config_list', description='Get the configuration settings for spyplane')
    async def spy_plane_config_list(self, interaction: discord.Interaction):
        config_dict_list = await get_all_configs()
        embed = discord.Embed(description='Getting configurations...', color=constants.EMBED_COLOUR_OK)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(title='Configurations', color=constants.EMBED_COLOUR_QU)
        for config_dict in config_dict_list:
            embed.add_field(name=config_dict.config_setting, value=config_dict.config_value)

        await interaction.delete_original_response()
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name='spy_plane_update_config', description='Update a configuration')
    async def spy_plane_update_config(self, interaction: discord.Interaction, config_setting: str, config_value: str):
        spam_channel = interaction.guild.get_channel(constants.channel_botspam())
        print(f'{interaction.user.name} called an update for the config {config_setting}')
        # check if config exists
        config_setting_exists = await find_config(config_setting)
        if not config_setting_exists:
            embed = discord.Embed(description='❓ **That config doesn\'t exist.**', color=constants.EMBED_COLOUR_QU)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await update_config(config_setting, config_value)
        embed = discord.Embed(description='✅ Config updated', color=constants.EMBED_COLOUR_OK)
        await interaction.response.send_message(embed=embed, ephemeral=True)

        spam_embed = discord.Embed(description=f'ℹ️ {interaction.user.mention} updated the config value '
                                               f'for {config_setting}')
        await spam_channel.send(embed=spam_embed)

    @app_commands.command(name='spy_plane_scouting_report', description='Outputs a csv of all scouts')
    async def spy_plane_scouting_report(self, interaction: discord.Interaction):
        await scouting_data_to_csv(interaction)
