# mod.py
import discord
from discord.ext import commands

class Mod(commands.Cog):
    """Cog wrapping administrative commands."""
    def __init__(self, bot):
        self.bot = bot

    def skipped_msg(ctx, members):
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
        return msg + '.'

    @commands.command()
    async def ban(self, ctx):
        """
        Bans tagged users from the guild.

        Requires Ban Users permission.
        """
        if not ctx.author.guild_permissions.ban_members:
            await ctx.message.add_reaction('\U0001F44E');
            await ctx.send("You lack this authority!")
            return

        mentions = ctx.message.mentions
        
        if mentions:
            skipped = []
            
            for user in mentions:
                try:
                    await user.ban()
                except discord.errors.HTTPException:
                    skipped.append(user)

            if not skipped:
                await ctx.send("All users successfully banned.")
            elif len(skipped) == len(mentions):
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("No users were banned.")
            else:
                await ctx.message.add_reaction('\u26A0');
                await ctx.send("Some user(s) successfully banned. "
                               f"{Moderator.skipped_msg(ctx, skipped)}")
        elif len(ctx.message.content.split()) > 1:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("Unrecognized user mention(s).")
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("No users mentioned.")
    
    @commands.command(aliases=['bo', 'sv', 'stopvid', 'stopvideo'])
    async def blackout(self, ctx):
        """
        Ends tagged users' streams.
        Achieved by moving them to a temporary channel, then moving them back.

        Requires Move Members permission.
        """
        if not ctx.author.guild_permissions.move_members:
            await ctx.message.add_reaction('\U0001F44E');
            await ctx.send("You lack this authority!")
            return
        
        mentions = ctx.message.mentions
        temp_channel = await ctx.guild.create_voice_channel('TEMP')
        
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
                await ctx.send("Some video stream(s) successfully moved. "
                               f"{Moderator.skipped_msg(ctx, skipped)}")
        elif len(ctx.message.content.split()) > 1:
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("Unrecognized user mention(s).")
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("No users mentioned.")

        await temp_channel.delete()

    @commands.command()
    async def deafen(self, ctx):
        """
        Server deafens a user.

        Requires Deafen Members permission.
        """
        if not ctx.author.guild_permissions.deafen_members:
            await ctx.message.add_reaction('\U0001F44E');
            await ctx.send("You lack this authority!")
            return

        mentions = ctx.message.mentions
        
        if mentions:
            for user in mentions:
                await user.edit(deafen=True)

            await ctx.send("Deafened user(s).")
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("No users mentioned.")
    
    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        """
        Disconnects tagged users from their voice channels.
        Achieved by moving them to a temporary channel, then deleting that
        channel.

        Requires Move Members permission.
        """
        if not ctx.author.guild_permissions.move_members:
            await ctx.message.add_reaction('\U0001F44E');
            await ctx.send("You lack this authority!")
            return
        
        mentions = ctx.message.mentions
        temp_channel = await ctx.guild.create_voice_channel('TEMP')
        
        if mentions:
            skipped = []
            
            for user in mentions:
                try:
                    await user.move_to(temp_channel)
                except discord.errors.HTTPException:
                    skipped.append(user)

            if not skipped:
                await ctx.send("All users successfully disconnected.")
            elif len(skipped) == len(mentions):
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("No users were disconnected.")
            else:
                await ctx.message.add_reaction('\u26A0');
                await ctx.send("Some user(s) successfully disconnected. "
                               f"{Moderator.skipped_msg(ctx, skipped)}")
        elif len(ctx.message.content.split()) > 1:
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("Unrecognized user mention(s).")
        else:
            try:
                await ctx.author.move_to(temp_channel)
                await ctx.send(f"Disconnected {ctx.author.mention}.")
            except discord.errors.HTTPException:
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("You were not in a voice channel.")
        
        await temp_channel.delete()

    @commands.command()
    async def kick(self, ctx):
        """
        Kicks tagged users from the guild.

        Requires Kick Members permission.
        """
        if not ctx.author.guild_permissions.kick_members:
            await ctx.message.add_reaction('\U0001F44E');
            await ctx.send("You lack this authority!")
            return

        mentions = ctx.message.mentions
        
        if mentions:
            skipped = []
            
            for user in mentions:
                try:
                    await user.kick()
                except discord.errors.HTTPException:
                    skipped.append(user)

            if not skipped:
                await ctx.send("All users successfully kicked.")
            elif len(skipped) == len(mentions):
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("No users were kicked.")
            else:
                await ctx.message.add_reaction('\u26A0');
                await ctx.send("Some user(s) successfully kicked. "
                               f"{Moderator.skipped_msg(ctx, skipped)}")
        elif len(ctx.message.content.split()) > 1:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("Unrecognized user mention(s).")
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("No users mentioned.")

    @commands.command()
    async def mute(self, ctx):
        """
        Server mutes a user.

        Requires Mute Members permission.
        """
        if not ctx.author.guild_permissions.mute_members:
            await ctx.message.add_reaction('\U0001F44E');
            await ctx.send("You lack this authority!")
            return

        mentions = ctx.message.mentions
        
        if mentions:
            for user in mentions:
                await user.edit(mute=True)

            await ctx.send("Muted user(s).")
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("No users mentioned.")

    @commands.command(aliases=['nick'])
    async def nickname(self, ctx, member:discord.Member, *, nick):
        """
        Changes a user's nickname.
        Changes the command author's nickname if nobody tagged.

        Requires Change Nickname permission.
        """
        if not (member == ctx.author or \
                ctx.author.guild_permissions.change_nickname):
            await ctx.message.add_reaction('\U0001F44E');
            await ctx.send("You lack this authority!")
            return

        try:
            old_nick = member.nick
            
            if nick == old_nick:
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("That's the same name.")
            else:
                await member.edit(nick=nick)
                await ctx.send(f"Updated nickname for {member.mention}.")
        except discord.errors.Forbidden:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("I don't have permission to do that.")

    @nickname.error
    async def nickname_err(self, ctx, err):
        if isinstance(err, commands.errors.MemberNotFound) or \
        isinstance(err, commands.errors.MissingRequiredArgument):
            nick_args = ctx.message.content.split()[1:]
            
            if 'member' in str(err) and not nick_args:
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("No user mentioned.")
            elif 'nick' in str(err):
                await ctx.send("No new nickname provided.")
            else:
                await self.nickname(ctx, ctx.author, ' '.join(nick_args))
                
    @commands.command()
    async def pin(self, ctx):
        """
        Pins the referenced message.

        Requires Delete Messages permission.
        """
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.message.add_reaction('\U0001F44E');
            await ctx.send("You lack this authority!")
            return
        
        ref = ctx.message.reference
        
        if ref and ref.message_id:
            target = await ctx.channel.fetch_message(ref.message_id)

            if target.pinned:
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("Message already pinned.")
            else:
                await target.pin()
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"No message referenced.")

    @commands.command(aliases=['drag'])
    async def summon(self, ctx):
        """
        Moves tagged users to author's voice channel.

        Requires Move Members permission.
        """
        if not ctx.author.guild_permissions.move_members:
            await ctx.message.add_reaction('\U0001F44E');
            await ctx.send("You lack this authority!")
            return
        
        mentions = ctx.message.mentions
        voice = ctx.author.voice

        if not (voice and voice.channel):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("You're not in a voice channel.")
            return
        
        if mentions:
            skipped = []
            
            for user in mentions:
                try:
                    await user.move_to(voice.channel)
                except discord.errors.HTTPException:
                    skipped.append(user)

            if not skipped:
                await ctx.send("All users successfully moved.")
            elif len(skipped) == len(mentions):
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("No users were moved.")
            else:
                await ctx.message.add_reaction('\u26A0');
                await ctx.send("Some user(s) successfully moved. "
                               f"{Moderator.skipped_msg(ctx, skipped)}")
        elif len(ctx.message.content.split()) > 1:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("Unrecognized user mention(s).")
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("No users mentioned.")

    @commands.command()
    async def unmute(self, ctx):
        """
        Server unmutes a user.

        Requires Mute Members permission.
        """
        if not ctx.author.guild_permissions.mute_members:
            await ctx.message.add_reaction('\U0001F44E');
            await ctx.send("You lack this authority!")
            return

        mentions = ctx.message.mentions
        
        if mentions:
            for user in mentions:
                await user.edit(mute=False)

            await ctx.send("Unmuted user(s).")
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("No users mentioned.")

    @commands.command()
    async def undeafen(self, ctx):
        """
        Server undeafens a user.

        Requires Deafen Members permission.
        """
        if not ctx.author.guild_permissions.deafen_members:
            await ctx.message.add_reaction('\U0001F44E');
            await ctx.send("You lack this authority!")
            return

        mentions = ctx.message.mentions
        
        if mentions:
            for user in mentions:
                await user.edit(deafen=False)

            await ctx.send("Undeafened user(s).")
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("No users mentioned.")

    @commands.command()
    async def unpin(self, ctx):
        """
        Unpins the referenced message.

        Requires Delete Messages permission.
        """
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.message.add_reaction('\U0001F44E');
            await ctx.send("You lack this authority!")
            return
        
        ref = ctx.message.reference
        
        if ref and ref.message_id:
            target = await ctx.channel.fetch_message(ref.message_id)

            if target.pinned:
                await target.unpin()
                await ctx.send("Message unpinned.")
            else:
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("Message not pinned.")
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"No message referenced.")
    
def setup(bot):
    bot.add_cog(Mod(bot))