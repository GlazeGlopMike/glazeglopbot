# glazeglopbot.py
import os
import discord
import dotenv

from discord.ext import commands

# set up client
dotenv.load_dotenv()
token = os.environ['DISCORD_TOKEN']
bot = commands.Bot(command_prefix='$')

dev_ids = []

async def is_dev(ctx):
    """
    Returns whether user is whitelisted as a developer.
    Sends error message if user isn't.
    """
    status = ctx.author.id in dev_ids
    
    if not status:
        await ctx.message.add_reaction('\U0001F44E');
        await ctx.send("You lack this authority!")
    
    return status

def load_dev_ids():
    """Loads whitelisted IDs from the DEV_IDS environment variable."""
    for dev_id in os.environ['DEV_IDS'].split(','):
        try:
            dev_ids.append(int(dev_id))
        except ValueError:
            print(f"Skipped invalid ID: '{dev_id}'")

@bot.command()
async def id(ctx):
    """Sends bot ID."""
    await ctx.send(f"My ID is {bot.user.id}.")

@bot.command(aliases=['ld'])
@commands.check(is_dev)
async def load(ctx, *, cog):
    """
    Loads a Discord cog.
    Restarts cog if already loaded,
    """
    try:
        bot.load_extension('cogs.' + cog)
        await ctx.send(f"Loaded cog '{cog}'.")
    except commands.ExtensionError as e:
        if "already" in str(e):
            await restart(ctx, cog=cog)
        elif 'raised an error' in str(e):
            await ctx.message.add_reaction('\U0001F916');
            await ctx.send(f"Couldn't load '{cog}' due to "
                           f"{repr(e.__cause__)}.")
        else:
            await ctx.message.add_reaction('\U0001F916');
            await ctx.send("Unrecognized cog.")

@bot.command(name='reload', aliases=['rld'])
@commands.check(is_dev)
async def restart(ctx, *, cog):
    """
    Reloads a Discord cog.
    Loads cog if not yet loaded.
    """
    if cog == '-all':
        await reload_all(ctx)
    else:
        try:
            bot.reload_extension('cogs.' + cog)
            await ctx.send(f"Reloaded cog '{cog}'.")
        except commands.ExtensionError as e:
            if 'has not been' in str(e):
                await load(ctx, cog=cog)
            elif 'raised an error' in str(e):
                await ctx.message.add_reaction('\U0001F916');
                await ctx.send(f"Couldn't reload '{cog}' due to "
                               f"{repr(e.__cause__)}.")
            else:
                await ctx.message.add_reaction('\U0001F916');
                await ctx.send("Unrecognized cog.")

@bot.command(name='reloadall', aliases=['rldall'])
@commands.check(is_dev)
async def reload_all(ctx):
    """Reloads all Discord cogs in the directory."""
    failed = []
    walk = os.walk('cogs')
    
    for path, subdirs, files in walk:
        for file in files:
            cog = file[:-3]
            
            if file.endswith('.py'):
                try:
                    bot.reload_extension(f'{path.replace("/", ".")}.{cog}')
                except commands.ExtensionError as e:
                    if 'has not been' in str(e):
                        bot.load_extension(f'{path.replace("/", ".")}.{cog}')
                    else:
                        failed.append(cog)
                except Exception:
                    failed.append(cog)

    if failed:
        if len(failed) == len(walk):
            await ctx.message.add_reaction('\U0001F916');
            await ctx.send("No cogs reloaded.")
        else:
            await ctx.message.add_reaction('\u26A0');
            await ctx.send(f"Some cogs not reloaded: {', '.join(failed)}.")
    else:
        await ctx.send("All cogs reloaded.")

@bot.command(aliases=['uld'])
@commands.check(is_dev)
async def unload(ctx, *, cog):
    """Unloads Discord cog."""
    try:
        bot.unload_extension('cogs.' + cog)
        await ctx.send(f"Unloaded cog '{cog}'.")
    except commands.ExtensionError:
        await ctx.message.add_reaction('\U0001F615');
        await ctx.send("Cog unrecognized or already inactive.")

@load.error
@restart.error
@unload.error
async def load_err(ctx, err):
    """Handles missing arguments by sending an error message."""
    if isinstance(err, commands.errors.MissingRequiredArgument):
        await ctx.message.add_reaction('\U0001F615');
        await ctx.send("Module name required.")
    else:
        print(err)

@bot.event
async def on_ready():
    """
    Triggered when bot connects to Discord.
    Prints a login message to the console.
    """
    print(f"{bot.user} ({bot.user.id}) connected to Discord.")

@bot.event
async def on_message(message):
    """
    Triggered when bot sees a new message.
    Ignores messages from bots.
    """
    if not message.author == bot.user or message.author.bot:
        await bot.process_commands(message)

# load all cogs in the directory on startup
for path, subdirs, files in os.walk('cogs'):
    for file in files:
        if file.endswith('.py'):
            cog = file[:-3]
            
            try:
                bot.load_extension(f'{path.replace("/", ".")}.{cog}')
            except Exception as e:
                print(f"Failed to load extension '{cog}': {str(e)}")

# load developer ids
load_dev_ids()

# run bot
try:
    bot.run(token)
except AttributeError:
    print("Login failed: Couldn't find the Discord token.")
except discord.errors.LoginFailure:
    print("Login failed: Invalid Discord token.")
