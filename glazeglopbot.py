# glazeglopbot.py
import datetime
import os

import discord
from discord.ext import commands
import dotenv

# setting up client
dotenv.load_dotenv()
token = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='$')

@bot.command()
async def load(ctx, *, cog):
    """Loads a Discord cog."""
    try:
        bot.load_extension('cogs.' + cog)
        await ctx.send(f"Loaded cog '{cog}'.")
    except commands.ExtensionError:
        if "already" in str(e):
            await restart(ctx, cog=cog)
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("Unrecognized cog.")

@bot.command(name='reload')
async def restart(ctx, *, cog):
    """Reloads a DIscord cog."""
    try:
        bot.reload_extension('cogs.' + cog)
        await ctx.send(f"Reloaded cog '{cog}'.")
    except commands.ExtensionError:
        await ctx.message.add_reaction('\U0001F615');
        await ctx.send("Unrecognized cog.")

@bot.command()
async def unload(ctx, *, cog):
    """Unloads a Discord cog."""
    try:
        bot.unload_extension('cogs.' + cog)
        await ctx.send(f"Unloaded cog '{cog}'.")
    except commands.ExtensionError:
        await ctx.message.add_reaction('\U0001F615');
        await ctx.send("Unrecognized cog.")

@load.error
@restart.error
@unload.error
async def load_err(ctx, err):
    """Handles missing arguments by sending an error message."""
    if isinstance(err, commands.errors.MissingRequiredArgument):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"Module name required.")

@bot.event
async def on_ready():
    """
    Triggered when bot connects to Discord.
    Writes a simple login message to the console.
    """
    print(f"{bot.user} connected to Discord.")

@bot.event
async def on_message(message):
    """Triggered when message sent in active channels."""

    # ignore messages from self and bots
    if message.author == bot.user or message.author.bot:
        return

    # allows commands to be processed
    await bot.process_commands(message)

# load all cogs in the directory
for path, subdirs, files in os.walk('cogs'):
    for file in files:
        if file[-3:] == '.py':
            try:
                bot.load_extension('cogs.' + file[:-3])
            except (AttributeError, ImportError):
                print(f"Failed to load extentsion '{ext}'.")

# start bot
bot.run(token)


