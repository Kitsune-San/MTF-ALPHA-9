import datetime
import discord
from discord import app_commands
from discord.ext import commands
import time
import platform
import utilities
from utilities import logname_pretty
current_uptime = time.time()


class botinfo(commands.Cog):
    """Bot information commands"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="botinfo", description="get bot information.")
    async def botinfo(self, interaction: discord.Interaction):
        discord_version = discord.__version__
        python_version = platform.python_version
        guilds = len(self.bot.guilds)
        current_time = time.time()
        difference = int(round(current_time - current_uptime))
        uptime = str(datetime.timedelta(seconds=difference))
        bot_version = utilities.bot_version
        embed = discord.Embed(title="Bot information",
                              color=discord.Color.blue())
        embed.add_field(name="Discord Version",
                        value=discord_version, inline=False)
        embed.add_field(name="Bot_version", value=bot_version, inline=False)
        embed.add_field(name="Guilds", value=guilds, inline=False)
        embed.add_field(name="Uptime", value=uptime, inline=False)
        await interaction.response.send_message(embed=embed)
        utilities.write_log(f"[{logname_pretty}]    {interaction.user} Requested bot information.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(botinfo(bot))
