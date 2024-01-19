#mod-points-bot.py
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import mod_points_db

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up the Discord objects
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

database = mod_points_db.ModPointsDb()

#Constants
NON_POSITIVE_INTEGER_STRING = f"The number must be a positive integer"
INTEGER_TOO_LARGE_STRING = f"The number selected is too large"
INVALID_USER_STRING = f"You cannot change your own points"
# String for mod point message. (Ex. @Albert gained 3 mod points)
SET_MOD_POINT_STRING = f"%s %s %d mod point(s)"
GET_MOD_POINT_STRING = f"%s has %d mod point(s)"
DATABASE_DOWN_STRING = f"The database is down. Contact crash2bandicoot."
DELETE_USER_WARNING_STRING = f"Stop trying to delete users"
SUCCESSFULLY_DELETED_USER_STRING = f"User removed successfully"
USER_SCORE_STRING = f"%s %d\n"

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")

def modify_points(ctx, user: discord.Member, points: int, isGive: bool):
    isPositive = True
    isOverflow = False
    isValidUser = True

    # Do not allow negative points
    if (points <= 0):
        isPositive = False
    elif(points > mod_points_db.POSTGRE_INT_MAX):
        isOverflow = True

    # Do not allow users to change their own points
    if (ctx.user.id == user.id):
        isValidUser = False
    
    embed = discord.Embed(
        color=discord.Color.blue(),
        title="Add Points" if isGive else "Remove Points"
    )

    isEphemeral = True
    if (not isPositive):
        embed.description = "%s" % NON_POSITIVE_INTEGER_STRING
    elif (isOverflow):
        embed.description = "%s" % INTEGER_TOO_LARGE_STRING
    elif (not isValidUser):
        embed.description = "%s" % INVALID_USER_STRING
    else:
        # Change the users points
        failure = database.setUserPoints(user.id, (points if isGive else (-1 * points)))
        
        if (failure):
            embed.description = DATABASE_DOWN_STRING
        else:
            isEphemeral = False
            embed.description = SET_MOD_POINT_STRING % (user.mention,
                                                        "gained" if isGive else "lost",
                                                        points)

    return [embed, isEphemeral]


@tree.command(
    name="add_points",
    description="Increase a user points"
)
async def add_points(ctx, user: discord.Member, points: int):
    [embed, isEphemeral] = modify_points(ctx, user, points, True)
    await ctx.response.send_message(embed = embed, ephemeral = isEphemeral)


@tree.command(
    name="remove_points",
    description="Remove a user's points"
)
async def remove_points(ctx, user: discord.Member, points: int):
    [embed, isEphemeral] = modify_points(ctx, user, points, False)
    await ctx.response.send_message(embed = embed, ephemeral = isEphemeral)

@tree.command(
    name="check_points",
    description="Check a user's points"
)
async def check_points(ctx, user: discord.Member = None):
    embed = discord.Embed(
        color=discord.Color.blue(),
        title='Check Points'
    )

    # If no user is selected, default to the invoker
    if user is None:
        user = ctx.user

    points = database.getUserPoints(user.id)
    embed.description = GET_MOD_POINT_STRING % (user.display_name, points)
    await ctx.response.send_message(embed = embed, ephemeral = True)

@tree.command(
    name="mod_leaderboard",
    description="Get the current Mod Point Leaderboard"
)
async def mod_leaderboard(ctx, is_visible: bool = False):
    embed = discord.Embed(
        color=discord.Color.blue(),
        title="Mod Point Leaderboard"
    )
    embed.description = ""
    userScores = database.getAllUserScores()
    userScores.sort(key=lambda a: a[1], reverse = True)

    for userScore in userScores:
        member = await ctx.guild.fetch_member(userScore[0])
        score = userScore[1]
        embed.description += USER_SCORE_STRING % (member.nick, score) 
 


    await ctx.response.send_message(embed = embed, ephemeral = not is_visible)

@tree.command(
    name="delete_user",
    description="Delete a user from the database"
)
async def delete_user(ctx, user: discord.Member):
    embed = discord.Embed(
        color=discord.Color.blue(),
        title="Delete User"
    )

    if (ctx.user.id == 175716657744969729):
        database.removeUser(user.id)
        embed.description = SUCCESSFULLY_DELETED_USER_STRING
    else:
        embed.description = DELETE_USER_WARNING_STRING
    await ctx.response.send_message(embed = embed, ephemeral = True)

client.run(TOKEN)
