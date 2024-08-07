#points_bot_core.py
import discord
from discord.ext import commands

from datetime import datetime

from .points_db import PointsDb

#Constants
NON_POSITIVE_INTEGER_STRING = f"The number must be a positive integer"
INTEGER_TOO_LARGE_STRING = f"The number selected is too large"
INVALID_USER_STRING = f"You cannot change your own points"
# String for point message. (Ex. @Albert gained 3 points)
SET_POINT_STRING = f"%s %s %d point(s)"
GET_POINT_STRING = f"%s has %d point(s)"
DATABASE_DOWN_STRING = f"The database is down. Contact crash2bandicoot."
DELETE_USER_WARNING_STRING = f"Stop trying to delete users"
SUCCESSFULLY_DELETED_USER_STRING = f"User removed successfully"
USER_SCORE_STRING = f"%s | %d\n"
COOLDOWN_STRING = f"%d minutes remaining on cooldown"

ADD_POINTS = True
REMOVE_POINTS = False

COOLDOWN = 5 # Cooldown in minutes

class PointsBotCore():

    def __init__(self, database: PointsDb):
        self.database = database
        self.cooldown_dict = {}

    def remaining_cooldown(self, user):
        cur_time = datetime.now()
        if user in self.cooldown_dict:
            last_time = self.cooldown_dict[user]
            return COOLDOWN - (cur_time-last_time).total_seconds()/60
        return 0
    
    def set_new_cooldown(self, user):
        self.cooldown_dict[user] = datetime.now()    

    def modify_points(self, interaction: discord.Interaction, user: discord.Member, points: int, isGive: bool):
        """Modifies the points of a user

        :param interaction: Represents the context in which a command is being invoked under
        :type interaction: discord.Interaction
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
        isEphemeral = True

        embed = discord.Embed(
            color=discord.Color.blue(),
            title="Add Points" if isGive else "Remove Points"
        )

        remaining_cooldown = self.remaining_cooldown(interaction.user)

        if remaining_cooldown > 0 :
            embed.description = COOLDOWN_STRING % remaining_cooldown
            return [embed, isEphemeral]

        self.set_new_cooldown(interaction.user)

        # Do not allow negative points
        if (points <= 0):
            isPositive = False
        elif(points > self.database.getIntMax()):
            isOverflow = True

        # Do not allow users to change their own points
        if (interaction.user.id == user.id):
            isValidUser = False

        
        if (not isPositive):
            embed.description = "%s" % NON_POSITIVE_INTEGER_STRING
        elif (isOverflow):
            embed.description = "%s" % INTEGER_TOO_LARGE_STRING
        elif (not isValidUser):
            embed.description = "%s" % INVALID_USER_STRING
        else:
            # Change the users points
            failure = self.database.setUserPoints(user.id, (points if isGive else (-1 * points)))

            if (failure):
                embed.description = DATABASE_DOWN_STRING
            else:
                isEphemeral = False
                embed.description = SET_POINT_STRING % (user.mention,
                                                            "gained" if isGive else "lost",
                                                            points)

        return [embed, isEphemeral]


    async def add_points(self, interaction: discord.Interaction, user: discord.Member, points: int):
        """Adds points to a user

        :param interaction: Represents the context in which a command is being invoked under
        :type interaction: discord.Interaction
        :param user: The user to add points to
        :type user: discord.Member
        :param points: The number of points to add
        :type points: int
        """
        [embed, isEphemeral] = self.modify_points(interaction, user, points, ADD_POINTS)
        await interaction.response.send_message(embed = embed, ephemeral = isEphemeral)


    async def remove_points(self, interaction: discord.Interaction, user: discord.Member, points: int):
        """Removes points from a user

        :param interaction: Represents the context in which a command is being invoked under
        :type interaction: discord.Interaction
        :param user: The user to remove points from
        :type user: discord.Member
        :param points: The number of points to remove
        :type points: int
        """
        [embed, isEphemeral] = self.modify_points(interaction, user, points, REMOVE_POINTS)
        await interaction.response.send_message(embed = embed, ephemeral = isEphemeral)

    async def check_points(self, interaction: discord.Interaction, user: discord.Member = None):
        """Checks the points of a user

        :param interaction: Represents the context in which a command is being invoked under
        :type interaction: discord.Interaction
        :param user: The user to check, defaults to None
        :type user: discord.Member, optional
        """
        embed = discord.Embed(
            color=discord.Color.blue(),
            title='Check Points'
        )

        # If no user is selected, default to the invoker
        if user is None:
            user = interaction.user

        points = self.database.getUserPoints(user.id)
        embed.description = GET_POINT_STRING % (user.display_name, points)
        await interaction.response.send_message(embed = embed, ephemeral = True)

    async def leaderboard(self, interaction: discord.Interaction, is_visible: bool = False):
        """Display the leaderboard of points

        :param interaction: Represents the context in which a command is being invoked under
        :type interaction: discord.Interaction
        :param is_visible: Sets whether the leaderboard embed is publically visible, defaults to False
        :type is_visible: bool, optional
        """
        embed = discord.Embed(
            color=discord.Color.blue(),
            title="Point Leaderboard"
        )
        embed.description = ""
        userScores = self.database.getAllUserScores()
        userScores.sort(key=lambda a: a[1], reverse = True)

        await interaction.response.defer()
        for userScore in userScores:
            score = userScore[1]
            member = await interaction.guild.fetch_member(userScore[0])
            name = member.nick if member.nick != None else member.name

            embed.description += USER_SCORE_STRING % (name, score)

        await interaction.followup.send(embed = embed, ephemeral = not is_visible)

    async def delete_user(self, interaction: discord.Interaction, user: discord.Member):
        """Delete a user from the database

        :param interaction: Represents the context in which a command is being invoked under
        :type interaction: discord.Interaction
        :param user: The user to remove from the database
        :type user: discord.Member
        """
        embed = discord.Embed(
            color=discord.Color.blue(),
            title="Delete User"
        )

        if (interaction.user.id == 175716657744969729):
            self.database.removeUser(user.id)
            embed.description = SUCCESSFULLY_DELETED_USER_STRING
        else:
            embed.description = DELETE_USER_WARNING_STRING
        await interaction.response.send_message(embed = embed, ephemeral = True)