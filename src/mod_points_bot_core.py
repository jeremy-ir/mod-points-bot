#mod_points_bot_core.py
import discord
from discord.ext import commands

from mod_points_db import ModPointsDb, POSTGRE_INT_MAX
database = ModPointsDb()

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

ADD_POINTS = True
REMOVE_POINTS = False

class ModPointsBot():

    def modify_points(self, ctx: commands.Context, user: discord.Member, points: int, isGive: bool):
        """Modifies the points of a user

        :param ctx: Represents the context in which a command is being invoked under
        :type ctx: commands.Context
        :param user: The user who's points will be changed
        :type user: discord.Member
        :param points: The number of points to change
        :type points: int
        :param isGive: Sets whether the points are going to be added or removed (True = added)
        :type isGive: bool
        :return: Return the new number of points the user has
        :rtype: int
        """        
        isPositive = True
        isOverflow = False
        isValidUser = True

        # Do not allow negative points
        if (points <= 0):
            isPositive = False
        elif(points > POSTGRE_INT_MAX):
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


    async def add_points(self, ctx: commands.Context, user: discord.Member, points: int):
        """Adds points to a user

        :param ctx: Represents the context in which a command is being invoked under
        :type ctx: commands.Context
        :param user: The user to add points to
        :type user: discord.Member
        :param points: The number of points to add
        :type points: int
        """
        [embed, isEphemeral] = self.modify_points(ctx, user, points, ADD_POINTS)
        await ctx.response.send_message(embed = embed, ephemeral = isEphemeral)


    async def remove_points(self, ctx: commands.Context, user: discord.Member, points: int):
        """Removes points from a user

        :param ctx: Represents the context in which a command is being invoked under
        :type ctx: commands.Context
        :param user: The user to remove points from
        :type user: discord.Member
        :param points: The number of points to remove
        :type points: int
        """
        [embed, isEphemeral] = self.modify_points(ctx, user, points, REMOVE_POINTS)
        await ctx.response.send_message(embed = embed, ephemeral = isEphemeral)

    async def check_points(self, ctx: commands.Context, user: discord.Member = None):
        """Checks the points of a user

        :param ctx: Represents the context in which a command is being invoked under
        :type ctx: commands.Context
        :param user: The user to check, defaults to None
        :type user: discord.Member, optional
        """          
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

    async def mod_leaderboard(self, ctx: commands.Context, is_visible: bool = False):
        """Display the leaderboard of points

        :param ctx: Represents the context in which a command is being invoked under
        :type ctx: commands.Context
        :param is_visible: Sets whether the leaderboard embed is publically visible, defaults to False
        :type is_visible: bool, optional
        """        
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

    async def delete_user(self, ctx: commands.Context, user: discord.Member):
        """Delete a user from the database

        :param ctx: Represents the context in which a command is being invoked under
        :type ctx: commands.Context
        :param user: The user to remove from the database
        :type user: discord.Member
        """        
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