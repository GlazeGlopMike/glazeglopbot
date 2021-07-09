# rng.py
import discord

from discord.ext import commands
from random import randint

class RNG(commands.Cog):
    """Cog wrapping randomizer commands."""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['dice','die'])
    async def roll(self, ctx, n:int=6):
        """Rolls an n-sided die."""
        try:
            await ctx.send(f"Rolled {randint(1, n)}.")
        except ValueError:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"Need a positive integer bound.")

    @roll.error
    async def rng_err(self, ctx, err):
        if isinstance(err, commands.errors.BadArgument):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"Illegal bound.")
    
def setup(bot):
    bot.add_cog(RNG(bot))
