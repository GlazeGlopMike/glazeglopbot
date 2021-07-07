# litwa.py
import discord
from discord.ext import commands

class Litwa(commands.Cog):
    """Cog wrapping litwa commands for the bros."""
    def __init__(self, bot):
        self.bot = bot

    def user_chain(self, users):
        """
        Accepts a list of Discord Member objects
        Returns a formatted str listing their tags"
        """
        if len(users) == 1:
            return f'{users[0].mention}'
        elif len(users) == 2:
            return f'{users[0].mention} and {users[1].mention}'
        elif len(users) > 2:
            users_cs = ""
            for user in users[:-1]:
                users_cs += f'{user.mention}, '
            return f'{users_cs}and {users[-1].mention}'
        else:
            return ""
        
    
    @commands.command()
    async def bontibi(self, ctx, *users: discord.Member):
        """
        Accepts a list of Discord Member objects.
        Greets tagged users, or the command author if none named.
        """
        mentions = ctx.message.mentions
        
        if mentions:
            tags = len(users)
            
            if tags == 1:
                await ctx.send(f"Bontibi, {users[0].mention}!")
            elif tags > 1:
                await ctx.send(f"Bonivobis, {self.user_chain(users)}!")
            
            else:
                await ctx.send(f"Bontibi, {ctx.author.mention}!")
        elif len(ctx.message.content.split()) > 1:
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send(f"Unrecognized user(s).")
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"No users mentioned.")
    
    @commands.command()
    async def gaeree(self, ctx, *users: discord.Member):
        """
        Accepts a list of Discord Member objects.
        Insults tagged users, or the command author if none named.
        """
        mentions = ctx.message.mentions
        
        if mentions:
            tags = len(users)
            
            if tags == 1:
                await ctx.send(f"{users[0].mention} is gaeree!")
            elif tags > 1:
                await ctx.send(f"{self.user_chain(users)} are gaeree!")
            else:
                await ctx.send(f"{ctx.author.mention} is gaeree!")
        elif len(ctx.message.content.split()) > 1:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"Unrecognized user(s).")
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"No users mentioned.")
    
    @bontibi.error
    @gaeree.error
    async def tag_err(self, ctx, err):
        """Handles unrecognized tags."""
        if isinstance(err, commands.errors.MemberNotFound):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"Couldn't find some of those users.")

    @commands.command()
    async def ree(self, ctx):
        """Sends a 'REE' text-to-speech message."""
        await ctx.send('REE-EEE-EEE-EEE-EEE-EEE!', tts=True)

def setup(bot):
    bot.add_cog(Litwa(bot))
