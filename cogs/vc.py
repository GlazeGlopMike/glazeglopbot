# vc.py
import discord
from discord.ext import commands

class VC(commands.Cog):
    """Cog wrapping voice channel commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['connect'])
    async def join(self, ctx):
        """Joins the author's voice channel."""
        voice = ctx.author.voice
        
        if not (voice and voice.channel):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("You're not in a voice channel.")
            return

        await voice.channel.connect()

    @commands.command()
    async def leave(self, ctx):
        """Disconnects the bot from its voice channel."""
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("Not in a voice channel.")
    
def setup(bot):
    bot.add_cog(VC(bot))
