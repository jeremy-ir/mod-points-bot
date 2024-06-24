#points-bot.py
import os

from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands

from .points_bot_core import PointsBotCore
from .points_db_postgres import PointsDbPostgres
from .points_db_test import PointsDbTest


# Set up the Discord objects
intents = discord.Intents.default()
client = discord.Client(intents=intents)

database = PointsDbPostgres()
#database = PointsDbTest()
pb = PointsBotCore(database)


class Points(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sync(self, ctx):
        fmt = await ctx.bot.tree.sync(guild = ctx.guild)
        await ctx.send(f"Synced {len(fmt)} commands to the current guild.")

    @app_commands.command(
        name="hello",
        description="Says hello"
    )
    @commands.is_owner()
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello", ephemeral = True)

    @app_commands.command(
        name="add_points",
        description="Increase a user points"
    )
    async def add_points(self, interaction: discord.Interaction, user: discord.Member, points: int):
        """Adds points to a user

        :param interaction: Represents the context in which a command is being invoked under
        :type interaction: discord.Interaction
        :param user: The user to add points to
        :type user: discord.Member
        :param points: The number of points to add
        :type points: int
        """
        await pb.add_points(interaction, user, points)


    @app_commands.command(
        name="remove_points",
        description="Remove a user's points"
    )
    async def remove_points(self, interaction: discord.Interaction, user: discord.Member, points: int):
        """Removes points from a user

        :param interaction: Represents the context in which a command is being invoked under
        :type interaction: discord.Interaction
        :param user: The user to remove points from
        :type user: discord.Member
        :param points: The number of points to remove
        :type points: int
        """
        await pb.remove_points(interaction, user, points)

    @app_commands.command(
        name="check_points",
        description="Check a user's points"
    )
    async def check_points(self, interaction: discord.Interaction, user: discord.Member = None):
        """Checks the points of a user

        :param interaction: Represents the context in which a command is being invoked under
        :type interaction: discord.Interaction
        :param user: The user to check, defaults to None
        :type user: discord.Member, optional
        """
        await pb.check_points(interaction, user)

    @app_commands.command(
        name="leaderboard",
        description="Get the current Point Leaderboard"
    )
    async def leaderboard(self, interaction: discord.Interaction, is_visible: bool = True):
        """Display the leaderboard of points

        :param interaction: Represents the context in which a command is being invoked under
        :type interaction: discord.Interaction
        :param is_visible: Sets whether the leaderboard embed is publically visible, defaults to False
        :type is_visible: bool, optional
        """
        await pb.leaderboard(interaction, is_visible)

    @app_commands.command(
        name="delete_user",
        description="Delete a user from the database"
    )
    async def delete_user(self, interaction: discord.Interaction, user: discord.Member):
        """Delete a user from the database

        :param interaction: Represents the context in which a command is being invoked under
        :type interaction: discord.Interaction
        :param user: The user to remove from the database
        :type user: discord.Member
        """
        await pb.delete_user(interaction, user)

async def setup(bot):
    guild_id = int(os.getenv('GUILD_ID'))
    await bot.add_cog(Points(bot), guilds = [discord.Object(id=guild_id)])
