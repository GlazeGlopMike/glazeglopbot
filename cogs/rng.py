# rng.py
import discord

from discord.ext import commands
from random import randint

class RNG(commands.Cog):
    """Cog wrapping randomizer commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='randint',aliases=['rndint'])
    async def randominteger(self, ctx, a:int=100, b:int=1):
        """
        Generates a random integer within the bounds (inclusive).
        
        Swaps values if given in descending order.
        Uses 1 as the lower bound one argument given.
        Uses 1 and 100 as the bounds if no arguments given.
        """
        if a > b:
            a, b = b, a
        
        await ctx.send(f"(int {a} to {b}): {randint(a, b)}")
    
    @commands.command(aliases=['dice','die'])
    async def roll(self, ctx, n:int=6):
        """Rolls an n-sided die."""
        try:
            await ctx.send(f"Rolled {randint(1, n)}.")
        except ValueError:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("Need a positive integer bound.")

    @randominteger.error
    @roll.error
    async def rng_err(self, ctx, err):
        """Handles argument errors."""
        if isinstance(err, commands.errors.BadArgument):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("Illegal bound.")
        elif isinstance(err, commands.errors.MissingRequiredArgument):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("Need an upper bound.")
    
def setup(bot):
    bot.add_cog(RNG(bot))
