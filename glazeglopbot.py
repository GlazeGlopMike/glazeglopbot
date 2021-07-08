# glazeglopbot.py
import os

import discord
from discord.ext import commands
import dotenv

# setting up client
dotenv.load_dotenv()
token = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='$')

@bot.command(aliases=['ld'])
async def load(ctx, *, cog):
    """Loads a Discord cog."""
    try:
        bot.load_extension('cogs.' + cog)
        await ctx.send(f"Loaded cog '{cog}'.")
    except commands.ExtensionError:
        if "already" in str(e): # restart if cog already loaded
            await restart(ctx, cog=cog)
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("Unrecognized cog.")

@bot.command(name='reload', aliases=['rld'])
async def restart(ctx, *, cog):
    """Reloads a Discord cog."""

    if cog == '-all':
        await reload_all(ctx)
    else:
        try:
            bot.reload_extension('cogs.' + cog)
            await ctx.send(f"Reloaded cog '{cog}'.")
        except commands.ExtensionError:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("Unrecognized cog.")

@bot.command(name='reloadall', aliases=['rldall'])
async def reload_all(ctx):
    """Reloads all DIscord cogs in the directory."""

    for path, subdirs, files in os.walk('cogs'):
        for file in files:
            if file[-3:] == '.py':
                try:
                    bot.reload_extension('cogs.' + file[:-3])
                except (AttributeError, ImportError, commands.ExtensionError):
                    print(f"Failed to reload extension '{file[:-3]}'.")
    
    await ctx.send(f"Reloaded cogs.")

@bot.command(name='reloadenv', aliases=['rldenv'])
async def reload_env(ctx):
    """Reloads tokens."""
    dotenv.load_dotenv()

@bot.command(aliases=['uld'])
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
    if not message.author == bot.user or message.author.bot:
        await bot.process_commands(message)

# load all cogs in the directory on startup
for path, subdirs, files in os.walk('cogs'):
    for file in files:
        if file[-3:] == '.py':
            try:
                bot.load_extension('cogs.' + file[:-3])
            except (AttributeError, ImportError, commands.ExtensionError):
                print(f"Failed to load extension '{ext}'.")

try:
    bot.run(token)
except AttributeError:
    print("Launch failed: Couldn't find the Discord token.")

