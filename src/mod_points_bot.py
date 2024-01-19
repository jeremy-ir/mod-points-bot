#mod-points-bot.py
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from mod_points_bot_core import ModPointsBot
from mod_points_db import ModPointsDb

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up the Discord objects
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

database = ModPointsDb()
mpb = ModPointsBot()


@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")

@tree.command(
    name="add_points",
    description="Increase a user points"
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
    await mpb.add_points(ctx, user, points)


@tree.command(
    name="remove_points",
    description="Remove a user's points"
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
    await mpb.remove_points(ctx, user, points)

@tree.command(
    name="check_points",
    description="Check a user's points"
)
async def check_points(ctx: commands.Context, user: discord.Member = None):
    """Checks the points of a user

    :param ctx: Represents the context in which a command is being invoked under
    :type ctx: commands.Context
    :param user: The user to check, defaults to None
    :type user: discord.Member, optional
    """          
    await mpb.check_points(ctx, user)

@tree.command(
    name="mod_leaderboard",
    description="Get the current Mod Point Leaderboard"
)
async def mod_leaderboard(ctx: commands.Context, is_visible: bool = False):
    """Display the leaderboard of points

    :param ctx: Represents the context in which a command is being invoked under
    :type ctx: commands.Context
    :param is_visible: Sets whether the leaderboard embed is publically visible, defaults to False
    :type is_visible: bool, optional
    """
    await mpb.mod_leaderboard(ctx, is_visible)

@tree.command(
    name="delete_user",
    description="Delete a user from the database"
)
async def delete_user(ctx: commands.Context, user: discord.Member):
    """Delete a user from the database

    :param ctx: Represents the context in which a command is being invoked under
    :type ctx: commands.Context
    :param user: The user to remove from the database
    :type user: discord.Member
    """  
    await mbp.delete_user(ctx, user)

client.run(TOKEN)
