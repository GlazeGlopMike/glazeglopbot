# moderator.py
import discord
from discord.ext import commands

class Admin(commands.Cog):
    """ Cog wrapping administrative commands. """
    def __init__(self, bot):
        self.bot = bot

    def skipped_msg(self, ctx, members):
        """
        Accepts a list of skipped Members.
        Sends a formatted message listing these users.
        """
        if not members:
            return
        
        msg = "Skipped: "
        if len(members) == 1:
            msg += members[0].name
        elif len(members) == 2:
            msg += f'{members[0].name} and {members[1].name}'
        elif len(members) > 2:
            for member in members[:-1]:
                msg += f'{member.name}, '
            msg += f'and {members[-1].name}'
        return msg
    
    @commands.command(aliases=['dc'])
    # @commands.has_permissions(move_members=True)
    async def disconnect(self, ctx):
        """
        Disconnects users from their voice channels by moving them to a
        temporary channel, then deleting that channel.
        
        Attempts to move tagged users, or the command author if none named.

        Requires Move Members permission.
        """

        # verify permissions
        if not ctx.author.guild_permissions.move_members:
            await ctx.message.add_reaction('\U0001F44E');
            ctx.send("You lack this authority!")
            return
        
        mentions = ctx.message.mentions
        temp_channel = await ctx.guild.create_voice_channel('KICK')
        
        if mentions:
            skipped = []
            
            for user in mentions:
                try:
                    await user.move_to(temp_channel)
                except discord.errors.HTTPException:
                    skipped.append(user)

            if not skipped:
                await ctx.send("All user(s) successfully disconnected.")
            elif len(skipped) == len(mentions):
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("No users were disconnected.")
            else:
                await ctx.message.add_reaction('\u26A0');
                await ctx.send(f"Some user(s) successfully disconnected. "
                               f"{self.skipped_msg(ctx, skipped)}")
        else:
            try:
                await ctx.author.move_to(temp_channel)
                await ctx.send(f"Disconnected {ctx.author.mention}.")
            except discord.errors.HTTPException:
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("You were not in a voice channel.")
        
        await temp_channel.delete()

def setup(bot):
    bot.add_cog(Admin(bot))
