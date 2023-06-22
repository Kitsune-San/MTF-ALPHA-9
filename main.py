from argparse import ArgumentParser
from typing import Optional
import discord
from discord.ext import commands
from discord.ext.commands import Context, Greedy
import assets
import utilities
from datetime import datetime
import logging
current_date_pretty = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
intents = discord.Intents.default()
intents.message_content = True
dev_mode = True
# Normal server 981259218122338354  |||||| Dev server
MY_GUILD = discord.Object(id=1038431009676460082)

parser = ArgumentParser(description="Run bot in development mode.")
parser.add_argument("--dev", action="store_true")
parser.add_argument("--disablelog", action="store_true", help="Disable the custom logger")
args = parser.parse_args()
appid = utilities.load_json(assets.jsonfiles)
appidnum = appid["appid"]

if args.dev:
    dev_mode = True

if dev_mode:
    appID = 860992699783839814
else:
    appID = 717708798483103764


class mtfbot(commands.Bot):
    def __init__(self, intents=intents):
        super().__init__(intents=intents, command_prefix=commands.when_mentioned,
                         application_id=appidnum, description="Praeparatus Esto")

    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=MY_GUILD)

    async def on_ready(self):
        link = utilities.load_json(assets.jsonfiles)
        linkurl = link["url"]
        if not args.disablelog:
            utilities.print_info_line(f"{self.user} has connected to the gateaway")
            utilities.print_info_line(linkurl)
        for extension in assets.modules:
            await bot.load_extension(extension)
            if not args.disablelog:
                utilities.print_info_line(f"Loaded {extension}")
                utilities.write_log(f"Loaded {extension}")
        await bot.change_presence(activity=discord.Game(name="Watching for new mtf cadets."))
        if not args.disablelog:
            utilities.print_info_line(f"Loaded Everything and bot is online")
            utilities.write_log(f"{self.user} is online from {current_date_pretty}")


bot = mtfbot(intents=intents)
bot.remove_command("help")
"""
*sync -> global sync
*sync guild -> sync current guild
*sync copy -> copies all global app commands to current guild and syncs
*sync delete -> clears all commands from the current guild target and syncs (removes guild commands)
*sync id_1 id_2 -> sync  guilds with 1 and 2
"""

1
@bot.command(name="synccmd")
@utilities.is_bot_admin()
async def sync(
        ctx: Context, guilds: Greedy[discord.Object], spec: Optional[str] = None) -> None:
    if not guilds:
        if spec == "guild":
            synced = await ctx.bot.tree.sync()
        elif spec == "copy":
            ctx.bot.tree.copy_global_to(guild=MY_GUILD)
            synced = await ctx.bot.tree.sync()
        elif spec == "delete":
            ctx.bot.tree.clear_commands()
            await ctx.bot.tree.sync()
            synced = []
        else:
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
            if not args.disablelog:
                utilities.print_info_line(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return
    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1
    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


json = utilities.load_json(assets.jsonfiles)
token = json["token"]
handler = discord.utils.setup_logging(level=logging.ERROR, root=False)

if not args.dev:
    if args.disablelog:
        utilities.print_warning_line("Disabled Custom cli logger. Raw errors/output will now be put to the console too.")
        bot.run(token)
    else:
        utilities.print_warning_line("Custom logger enabled.")
        bot.run(token, log_handler=handler)
else:
    if args.disablelog:
        utilities.print_warning_line("Disabled custom cli logger. Raw errors/output will now be put to the console too.")
        #bot.run(dev_token)
    else:
        utilities.print_warning_line("Custom logger enabled.")
       # bot.run(dev_token, log_handler=handler)

