import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import choices, Choice
import utilities
import assets


class faqs(commands.Cog):
    """Frequently asked questions links and information"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    
    @app_commands.command(name="links", description="Get the most asked links by chosing an option from the menu")
    @utilities.check_blacklist()
    @app_commands.describe(topic="The topic you want to view")
    @app_commands.choices(topic = [
        Choice(name="Personnel", value="https://mtfalpha9.eu/personnel/"),
        Choice(name="Website", value="https://mtfalpha9.eu"),
        Choice(name="Contact", value="https://mtfalpha9.eu/contact/"),
        Choice(name="Sign up", value ="https://mtfalpha9.eu/wp-login.php?redirect_to=https%253A%252F%252Fmtfalpha9.eu%252F")
    ])
    async def topic(self, interaction: discord.Interaction, topic:str): 
        utilities.print_info_line(f"{topic} requessted by {interaction.user}")
        return await interaction.response.send_message(topic, ephemeral=True)



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(faqs(bot))