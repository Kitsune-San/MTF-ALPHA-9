import json
import sqlite3
from colorama import Fore
import aiosqlite
import discord
from datetime import datetime
from discord import app_commands
logname = datetime.now()
logname_pretty = logname.strftime("%d-%m-%Y")
bot_version = "0.8.4"


async def connect_database():
    return await aiosqlite.connect("./database.db")


def load_json(path):
    with open(path) as f:
        return json.load(f)


def is_bot_admin():
    async def predicate(interaction: discord.Interaction):
        if is_bot_developer(interaction.user.id):
            return True
    return app_commands.check(predicate)


def is_bot_developer(member_id):
    database = sqlite3.connect("./database.db")
    try:
        listdevs = database.execute(
            f"SELECT * FROM botdevs WHERE userid = {member_id}")
        returndevs = listdevs.fetchall()
        if not returndevs:
            database.close()
            return False
        else:
            database.close()
            return True
    except ValueError:
        pass


async def get_prefix(_bot, message):
    for guild in _bot.guilds:
        db = await aiosqlite.connect("./database.db")
        try:
            await db.execute("CREATE TABLE IF NOT EXISTS guilds (guildID INT PRIMARY KEY, prefix text)")
            await db.commit()
        except ValueError:
            pass
        async with db.execute("SELECT prefix FROM guilds WHERE guildID = ?", (guild.id,)) as cursor:
            async for entry in cursor:
                prefix = entry
                return prefix
    try:
        await db.close()
    except ValueError:
        pass


async def on_guild_join(guild):
    database = await aiosqlite.connect("./database.db")
    try:
        await database.execute("CREATE TABLE IF NOT EXISTS guilds (guildID INT PRIMARY KEY, prefix text)")
        await database.commit()
        await database.execute("INSERT OR IGNORE INTO guilds VALUES (?, ?)", (guild.id, "ks-"))
        await database.commit()
        await database.close()
    except ValueError:
        pass


def create_embed(title, color):
    """Creates a Discord embed and returns it (for potential additional modification)"""
    embed = discord.Embed(title=title, color=color)
    return embed


def embed_add_field(embed, title, content, inline=True):
    """Helper function to add an additional field to an embed"""
    embed.add_field(name=title, value=content, inline=inline)


def create_simple_embed(title, color, field_title, field_content):
    """Creates a simple embed with only 1 field"""
    embed = create_embed(title, color)
    embed_add_field(embed, field_title, field_content)
    return embed

def write_log(message):
    """Writes information to the log file of the current day."""
    with open(f"./logs/{logname_pretty}.log", "a+") as f:
        f.writelines(message + "\n")
        f.close()



def print_info_line(message):
    """Prints a fancy info message."""
    print(Fore.GREEN + "[INFO]    "+ Fore.RESET + message)

def print_warning_line(message):
    """Prints a fancy warning message"""
    print(Fore.YELLOW + "[WARNING]   " + Fore.RESET + message) 

def print_exception_msg(message):
    """Prints a fancy exception message."""
    print(Fore.RED + "[ERROR]    " + Fore.RESET + message)


def check_blacklist():
    """Check used by the bot to see if a user is blacklisted. If check failed will inform the user about the blacklist.Uses `is_blacklisted()`"""
    async def precheck(interaction : discord.Interaction):
        if is_blacklisted(interaction.user.id):
            return False
        return True
    return app_commands.check(precheck)

def is_blacklisted(memberid):
    """Database check for blacklisted bot users."""
    database = sqlite3.connect("./database.db")
    database.execute("CREATE TABLE IF NOT EXISTS blacklist (memberid INTEGER PRIMARY KEY, name TEXT, number TEXT, reason TEXT, duration TEXT)")
    database.commit()
    try:
        list_users = database.execute("SELECT * FROM blacklist WHERE memberid = ?", (memberid,))
        return_users = list_users.fetchall()
        if return_users:
            database.close()
            return True
        else:
            database.close()
            return False
    except ValueError:
        pass