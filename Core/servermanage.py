import discord
from discord import app_commands
from discord.ext import commands
import assets
import utilities as  utils 
from typing import Optional
from discord.app_commands import choices, Choice
import aiosqlite
from sqlite3 import IntegrityError as duplicate_error
class serverowners(commands.Cog):
    """Specific server mamage commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    

    @app_commands.command(name="setuplogs", description="Set up logging channels.")
    @utils.check_blacklist()
    @app_commands.describe(messages = "The channel for message logs", users = "The channel for user logs")
    async def setuplogs(self,  interaction : discord.Interaction, messages:discord.TextChannel, users:discord.TextChannel):
        if not interaction.user.guild_permissions.ban_members:
            return await interaction.response.send_message("Only people who can ban users can use this command")
        else:
            db = await utils.connect_database()
            await db.execute("CREATE TABLE IF NOT EXISTS logchannels (guildid INTEGER PRIMARY KEY, messages TEXT, users TEXT)")
            await db.commit()
            try:
                await db.execute("INSERT INTO logchannels VALUES (?, ?, ?)", (interaction.guild.id, messages.id, users.id,))
            except duplicate_error:
                try:
                    await db.close()
                except ValueError:
                    pass
                return await interaction.response.send_message("It seems you already have log channels existing dummy! Use /editlogs instead.")
            await db.commit()
            try:
                await db.close()
            except ValueError:
                pass
            return await interaction.response.send_message(f"Setup successful, Set message logs to {messages.mention} and user logs to {users.mention}", ephemeral=True)
        


    @app_commands.command(name="editlogs", description="Edit the log channels of your server.")
    @app_commands.describe(messages = "The message log channel", users = "The user log channels.")
    async def editlogs(self, interaction : discord.Interaction, messages: Optional[discord.TextChannel], users: Optional[discord.TextChannel]):
        if not interaction.user.guild_permissions.ban_members:
            return await interaction.response.send_message("Only people who can ban users can use this command")
        else:
            db = await utils.connect_database()
            check = await db.execute("SELECT messages FROM logchannels WHERE guildid = ?", (interaction.guild.id,))
            check_result = await check.fetchone()
            if not check_result:
                if messages is not None and users is not None:
                    await db.execute("INSERT INTO logchannels VALUES (?, ?, ?)", (interaction.guild.id, messages.id, users.id,))
                    await db.commit()
                    try:
                        await db.close()
                    except ValueError:
                        pass
                    return await interaction.response.send_message(f"It seems you did not have log channels yet. Added {messages.mention} as the message log and {users.mention} as the user log channel since you provided these.", ephemeral=True)
                else:
                    try:
                        await db.close()
                    except ValueError:
                        pass
                    return await interaction.response.send_message("Sorry you do not have logs set up yet. And you did not provide enough channels to set them up (2 required.) Use /setuplogs instead!")
            else:
                if messages is not None:
                    if users is not None:
                        await db.execute(f"UPDATE logchannels SET messages = {messages.id} WHERE guildid = ?", (interaction.guild.id,))
                        await db.commit()
                        await db.execute(f"UPDATE logchannels SET users = {users.id} WHERE guildid = ?", (interaction.guild.id,))
                        await db.commit()
                        try:
                            await db.close()
                        except ValueError:
                            pass
                        return await interaction.response.send_message(f"Updated the channels. Messages are now logged in {messages.mention} and users are now logged in {users.mention}", ephemeral=True)
                    else:
                        await db.execute(f"UPDATE logchannels SET messages = {messages.id} WHERE guildid = ?", (interaction.guild.id,))
                        await db.commit()
                        try:
                            await db.close()
                        except ValueError:
                            pass
                        return await interaction.response.send_message(f"Updated the Message log channel to {messages.mention}", ephemeral=True)
                else:
                    if users is not None:
                        await db.execute(f"UPDATE logchannels SET users = {users.id} WHERE guildid = ?", (interaction.guild.id,))
                        await db.commit()
                        try:
                            await db.close()
                        except ValueError:
                            pass
                        return await interaction.response.send_message(f"Updated the user log channel to {users.mention}", ephemeral=True)
                if messages == None and users == None:
                    try:
                        await db.close()
                    except ValueError:
                        pass
                    return await interaction.response.send_message("Dummy, you forgot to provide channels to update")

    @app_commands.command(name="clearlogs", description="Remove all log channels stored in our database.")
    async def clearlogs(self, interaction : discord.Interaction):
        if not interaction.user.guild_permissions.ban_members:
            return await interaction.response.send_message("Only people who can ban users can use this command")
        else:
            db = await utils.connect_database()
            try:
                await db.execute("DELETE FROM logchannels WHERE guildid = ?", (interaction.guild.id,))
            except aiosqlite.OperationalError:
                try:
                    await db.close()
                except ValueError:
                    pass
                return await interaction.response.send_message(f"You do not have any logs set up!", ephemeral=True)
            await db.commit()
            try:
                await db.close()
            except ValueError:
                pass
            return await interaction.response.send_message("Deleted your log channels.", ephemeral=True)



    @commands.Cog.listener()
    async def on_message_delete(self, message):
        db = await utils.connect_database()
        Delete_embed = discord.Embed(title=f"Message deleted by {message.author.name}", color=discord.Color.red())
        Delete_embed.set_thumbnail(url=message.author.avatar.url)
        logchannel = await db.execute("SELECT messages FROM logchannels WHERE guildid = ?", (message.guild.id,))
        logchannel_result = await logchannel.fetchone()
        if message.author.bot:
            return
        if message.guild is None:
            return
        if logchannel_result is not None:
            channel = self.bot.get_channel(int(logchannel_result[0]))
            Delete_embed.add_field(name="Deleted message:", value=message.content, inline=False)
            Delete_embed.add_field(name="Author ID:", value=message.author.id)
            Delete_embed.add_field(name="Channel:", value=message.channel.mention)
            await channel.send(embed = Delete_embed)
            try:
                await db.close()
            except ValueError:
                pass
        else:
            try:
                await db.close()
            except ValueError:
                pass
            return
    
    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        db = await utils.connect_database()
        edit_embed = discord.Embed(title=f"Message edited by {message_after.author.name}", color = discord.Color.orange())
        logchannel = await db.execute("SELECT messages FROM logchannels WHERE guildid = ?", (message_after.guild.id,))
        logchannel_result = await logchannel.fetchone()
        if message_after.author.bot:
            return
        if message_after.guild is None:
            return
        if logchannel_result is not None:
            channel = self.bot.get_channel(int(logchannel_result[0]))
            edit_embed.set_thumbnail(url=message_after.author.avatar.url)
            edit_embed.add_field(name="Before:", value=message_before.content, inline=False)
            edit_embed.add_field(name="After:", value=message_after.content, inline=False)
            edit_embed.add_field(name="Author ID:", value=message_after.author.id, inline=False)
            edit_embed.add_field(name="Channel:", value=message_after.channel.mention, inline=False)
            await channel.send(embed = edit_embed)
            try:
                await db.close()
            except ValueError:
                pass
        else:
            try:
                await db.close()
            except ValueError:
                pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(serverowners(bot))
