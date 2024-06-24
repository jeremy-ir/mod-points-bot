import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import pathlib

def main():
    load_dotenv()
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    guild_id = int(os.getenv('GUILD_ID'))
    guild = bot.get_guild(guild_id)


    @bot.event
    async def on_ready():
        print("Hello World!")

        # Load all Cogs
        cur_path = pathlib.Path(__file__).parent.resolve()

        for filename in os.listdir(cur_path.joinpath("cogs")):
            await bot.load_extension(f"cogs.{filename}.cog")

        await bot.tree.sync(guild = guild)


    @bot.tree.command(name="load",
        description="Load a cog/extension"
    )
    @commands.is_owner()
    async def load(interaction: discord.Interaction, cog: str):
        await bot.load_extension(f"cogs.{cog.lower()}.cog")
        await bot.tree.sync(guild = guild)
        await interaction.response.send_message("Looaded extension", ephemeral = True)

    @bot.tree.command(name="unload",
        description="Unoad a cog/extension"
    )
    @commands.is_owner()
    async def unload(interaction: discord.Interaction, cog: str):
        await bot.unload_extension(f"cogs.{cog.lower()}.cog")
        await interaction.response.send_message("Unloaded extension", ephemeral = True)

    @bot.tree.command(name="reload",
        description="Reload a cog/extension"
    )
    @commands.is_owner()
    async def reload(interaction: discord.Interaction, cog: str):
        await bot.reload_extension(f"cogs.{cog.lower()}.cog")
        await bot.tree.sync(guild = guild)
        await interaction.response.send_message("Reloaded extension", ephemeral = True)

    @bot.tree.command(name="ping",
        description="Check if the bot is alive"
    )
    @commands.is_owner()
    async def ping(interaction: discord.Interaction):
        """ Answers with pong """
        await interaction.response.send_message("Alive", ephemeral = True)

    bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    main()