#points-bot.py
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from points_bot_core import PointsBot
from points_db_postgres import PointsDbPostgres
from points_db_test import PointsDbTest

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up the Discord objects
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

database = PointsDbPostgres()
#database = PointsDbTest()
pb = PointsBot(database)


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1253902922643931227))
    print("Ready!")



@tree.command(
    name="add_points",
    description="Increase a user points",
    guild=discord.Object(id=1253902922643931227)
)
async def add_points(ctx: commands.Context, user: discord.Member, points: int):
    """Adds points to a user

    :param ctx: Represents the context in which a command is being invoked under
    :type ctx: commands.Context
    :param user: The user to add points to
    :type user: discord.Member
    :param points: The number of points to add
    :type points: int
    """
    await pb.add_points(ctx, user, points)


@tree.command(
    name="remove_points",
    description="Remove a user's points",
    guild=discord.Object(id=1253902922643931227)
)
async def remove_points(ctx: commands.Context, user: discord.Member, points: int):
    """Removes points from a user

    :param ctx: Represents the context in which a command is being invoked under
    :type ctx: commands.Context
    :param user: The user to remove points from
    :type user: discord.Member
    :param points: The number of points to remove
    :type points: int
    """
    await pb.remove_points(ctx, user, points)

@tree.command(
    name="check_points",
    description="Check a user's points",
    guild=discord.Object(id=1253902922643931227)
)
async def check_points(ctx: commands.Context, user: discord.Member = None):
    """Checks the points of a user

    :param ctx: Represents the context in which a command is being invoked under
    :type ctx: commands.Context
    :param user: The user to check, defaults to None
    :type user: discord.Member, optional
    """
    await pb.check_points(ctx, user)

@tree.command(
    name="leaderboard",
    description="Get the current Point Leaderboard",
    guild=discord.Object(id=1253902922643931227)
)
async def leaderboard(ctx: commands.Context, is_visible: bool = False):
    """Display the leaderboard of points

    :param ctx: Represents the context in which a command is being invoked under
    :type ctx: commands.Context
    :param is_visible: Sets whether the leaderboard embed is publically visible, defaults to False
    :type is_visible: bool, optional
    """
    await pb.leaderboard(ctx, is_visible)

@tree.command(
    name="delete_user",
    description="Delete a user from the database",
    guild=discord.Object(id=1253902922643931227)
)
async def delete_user(ctx: commands.Context, user: discord.Member):
    """Delete a user from the database

    :param ctx: Represents the context in which a command is being invoked under
    :type ctx: commands.Context
    :param user: The user to remove from the database
    :type user: discord.Member
    """
    await pb.delete_user(ctx, user)

client.run(TOKEN)
