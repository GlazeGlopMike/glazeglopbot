# moderator.py
import discord
from discord.ext import commands

class Moderator(commands.Cog):
    """Cog wrapping administrative commands."""
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

    @commands.command(aliases=['bo', 'sv', 'stopvid', 'stopvideo'])
    async def blackout(self, ctx):
        """
        Ends tagged users' streams by moving them to a temporary channel, then  
        moving them back.

        Requires Move Members permission.
        """
        # verify permissions
        if not ctx.author.guild_permissions.move_members:
            await ctx.message.add_reaction('\U0001F44E');
            await ctx.send("You lack this authority!")
            return
        
        mentions = ctx.message.mentions
        temp_channel = await ctx.guild.create_voice_channel('BLACKOUT')
        
        if mentions:
            skipped = []
            
            for user in mentions:
                voice = user.voice

                if not (voice and voice.channel):
                    skipped.append(user)
                    continue
                
                try:
                    channel = voice.channel
                    await user.move_to(temp_channel)
                    await user.move_to(channel)
                except discord.errors.HTTPException:
                    skipped.append(user)

            if not skipped:
                await ctx.send("All video streams successfully stopped.")
            elif len(skipped) == len(mentions):
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("No video streams were stopped.")
            else:
                await ctx.message.add_reaction('\u26A0');
                await ctx.send(f"Some video stream(s) successfully moved. "
                               f"{self.skipped_msg(ctx, skipped)}")
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"No users specified.")

        await temp_channel.delete()
    
    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        """
        Disconnects tagged users from their voice channels by moving them to a 
        temporary channel, then deleting that channel.

        Requires Move Members permission.
        """

        # verify permissions
        if not ctx.author.guild_permissions.move_members:
            await ctx.message.add_reaction('\U0001F44E');
            await ctx.send("You lack this authority!")
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

    @commands.command(aliases=['drag'])
    async def summon(self, ctx):
        """
        Moves users to author's voice channel.

        Requires Move Members permission.
        """
        # verify permissions
        if not ctx.author.guild_permissions.move_members:
            await ctx.message.add_reaction('\U0001F44E');
            await ctx.send("You lack this authority!")
            return
        
        mentions = ctx.message.mentions
        voice = ctx.author.voice

        if not (voice and voice.channel):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("You were not in a voice channel.")
            return
        
        if mentions:
            skipped = []
            
            for user in mentions:
                try:
                    await user.move_to(voice.channel)
                except discord.errors.HTTPException:
                    skipped.append(user)

            if not skipped:
                await ctx.send("All user(s) successfully moved.")
            elif len(skipped) == len(mentions):
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("No users were moved.")
            else:
                await ctx.message.add_reaction('\u26A0');
                await ctx.send(f"Some user(s) successfully moved. "
                               f"{self.skipped_msg(ctx, skipped)}")
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"No users specified.")

def setup(bot):
    bot.add_cog(Moderator(bot))
