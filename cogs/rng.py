# rng.py
import discord

from discord.ext import commands
from random import random

class RNG(commands.Cog):
    """Cog wrapping randomizer commands."""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def roll(self, ctx, n:int=6):
        """Rolls an n-sided die."""
        result = randint(1, n)
        await ctx.send(f"Rolled {result}.")

def setup(bot):
    bot.add_cog(RNG(bot))
