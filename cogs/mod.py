# mod.py
import discord
from discord.ext import commands

def skipped_msg(ctx, members):
    """Returns formatted message listing users."""
    if not members:
        return ''
    
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

def partial_perms_ok(ctx):
    """
    Returns whether the user can use command on self without full permissions.
    True if user doesn't tag anyone or tags themselves only.
    """
    mentions = ctx.message.mentions
    
    return (len(mentions) == 1 and mentions[0] == ctx.author
            or not bool(mentions))

async def validate(ctx, perm, *, allow_self=False, guild_only=False):
    """
    Returns whether user can use command in context.
    Sends error message if authorization fails.

    Use on self not allowed by default.
    Commands allowed in DMs by default.
    """
    if guild_only and not ctx.guild:
        await ctx.message.add_reaction('\U0001F615')
        await ctx.send("Not in a guild.")
        return False
    elif ctx.guild and not (getattr(ctx.author.guild_permissions, perm)
                            or partial_perms_ok(ctx)):
        await ctx.message.add_reaction('\U0001F44E')
        await ctx.send("You lack this authority.")
        return False

    return True

class Mod(commands.Cog):
    """Cog wrapping administrative commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ban(self, ctx):
        """
        Bans tagged users from guild.

        Requires Ban Users permission.
        """
        if not await validate(ctx, 'ban_members', guild_only=True):
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
                await ctx.message.add_reaction('\U0001F615')
                await ctx.send("No users were banned.")
            else:
                await ctx.message.add_reaction('\u26A0')
                await ctx.send("Some user(s) successfully banned. "
                               f"{skipped_msg(ctx, skipped)}.")
        elif len(ctx.message.content.split()) > 1:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("Unrecognized user mention(s).")
        else:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("No users mentioned.")
    
    @commands.command(aliases=['bo', 'sv', 'stopvid', 'stopvideo'])
    async def blackout(self, ctx):
        """
        Ends tagged users' streams.
        Moves users to temporary channel, then back.

        Requires Move Members permission, unless used on self.
        """
        mentions = ctx.message.mentions
        
        if not await validate(ctx, 'move_members', allow_self=True,
                              guild_only=True):
            return
        
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
                await ctx.message.add_reaction('\U0001F615')
                await ctx.send("No video streams were stopped.")
            else:
                await ctx.message.add_reaction('\u26A0')
                await ctx.send("Some video stream(s) successfully moved. "
                               f"{skipped_msg(ctx, skipped)}.")
        elif len(ctx.message.content.split()) > 1:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("Unrecognized user mention(s).")
        else:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("No users mentioned.")

        await temp_channel.delete()

    @commands.command()
    async def deafen(self, ctx):
        """
        Server deafens a user.

        Requires Deafen Members permission.
        """
        if not await validate(ctx, 'deafen_members', allow_self=True,
                              guild_only=True):
            return

        mentions = ctx.message.mentions
        
        if mentions:
            for user in mentions:
                await user.edit(deafen=True)

            await ctx.send("Server deafened user(s).")
        else:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send(f"Server deafened {ctx.author.mention}.")
    
    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        """
        Disconnects tagged users from their voice channels.

        Requires Move Members permission, unless used on self.
        """
        mentions = ctx.message.mentions
        
        if not await validate(ctx, 'move_members', allow_self=True,
                              guild_only=True):
            return
        
        if mentions:
            skipped = []
            
            for user in mentions:
                try:
                    await user.move_to(None)
                except discord.errors.HTTPException:
                    skipped.append(user)

            if not skipped:
                await ctx.send("All users successfully disconnected.")
            elif len(skipped) == len(mentions):
                await ctx.message.add_reaction('\U0001F615')
                await ctx.send("No users were disconnected.")
            else:
                await ctx.message.add_reaction('\u26A0')
                await ctx.send("Some user(s) successfully disconnected. "
                               f"{skipped_msg(ctx, skipped)}.")
        elif len(ctx.message.content.split()) > 1:
                await ctx.message.add_reaction('\U0001F615')
                await ctx.send("Unrecognized user mention(s).")
        else:
            try:
                await ctx.author.move_to(None)
                await ctx.send(f"Disconnected {ctx.author.mention}.")
            except discord.errors.HTTPException:
                await ctx.message.add_reaction('\U0001F615')
                await ctx.send("You were not in a voice channel.")

    @commands.command()
    async def kick(self, ctx):
        """
        Kicks tagged users from guild.

        Requires Kick Members permission.
        """
        if not await validate(ctx, 'kick_members', guild_only=True):
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
                await ctx.message.add_reaction('\U0001F615')
                await ctx.send("No users were kicked.")
            else:
                await ctx.message.add_reaction('\u26A0')
                await ctx.send("Some user(s) successfully kicked. "
                               f"{skipped_msg(ctx, skipped)}.")
        elif len(ctx.message.content.split()) > 1:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("Unrecognized user mention(s).")
        else:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("No users mentioned.")

    @commands.command()
    async def mute(self, ctx):
        """
        Server mutes user.

        Requires Mute Members permission.
        """
        if not await validate(ctx, 'mute_members', guild_only=True):
            return

        mentions = ctx.message.mentions
        
        if mentions:
            for user in mentions:
                await user.edit(mute=True)

            await ctx.send("Server muted user(s).")
        else:
            await ctx.author.edit(mute=True)
            await ctx.send(f"Server muted {ctx.author.mention}.")

    @commands.command(aliases=['nick'])
    async def nickname(self, ctx, member:discord.Member, *, nick):
        """
        Changes user's nickname.
        Changes command author's nickname if nobody tagged.

        Requires Manage Nickname permission if used on others.
        Requires Change Nickname permission if used on self.
        """
        author = ctx.author
        if not ((member == author and author.guild_permissions.change_nickname)
                or ctx.author.guild_permissions.manage_nicknames):
            await ctx.message.add_reaction('\U0001F44E')
            await ctx.send("You lack this authority!")
            return

        try:
            old_nick = member.nick
            
            if nick == old_nick:
                await ctx.message.add_reaction('\U0001F615')
                await ctx.send("That's the same name.")
            else:
                await member.edit(nick=nick)
                await ctx.send(f"Updated nickname for {member.mention}.")
        except discord.errors.Forbidden:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("I don't have permission to do that.")

    @nickname.error
    async def nickname_err(self, ctx, err):
        """Handles argument errors."""
        if (isinstance(err, commands.errors.MemberNotFound)
        or isinstance(err, commands.errors.MissingRequiredArgument)):
            nick_args = ctx.message.content.split()[1:]
            
            if 'Member' in str(err) and not nick_args:
                await ctx.message.add_reaction('\U0001F615')
                await ctx.send("No user mentioned.")
            elif 'nick' in str(err):
                await ctx.send("No new nickname provided.")
            else:
                await self.nickname(ctx, ctx.author, nick=' '.join(nick_args))
                
    @commands.command()
    async def pin(self, ctx):
        """
        Pins referenced message.

        Requires Delete Messages permission.
        """
        if not await validate(ctx, 'manage_messages'):
            return
        
        ref = ctx.message.reference
        
        if ref and ref.message_id:
            target = await ctx.channel.fetch_message(ref.message_id)

            if target.pinned:
                await ctx.message.add_reaction('\U0001F615')
                await ctx.send("Message already pinned.")
            else:
                await target.pin()
                await ctx.send("Message pinned.")
        else:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send(f"No message referenced.")
    
    @commands.command()
    async def profile(self, ctx, member:discord.Member):
        """Profiles user."""
        if not await validate(ctx, 'send_messages', guild_only=True):
            return
        
        joined = member.joined_at
        join_str = joined.strftime('%Y-%m-%d') if joined else '--'
        roles = [role.name for role in member.roles[1:]]
        highest_role = roles[-1] if roles else '--'
        other_roles = ', '.join(roles[:-1]) if len(roles) > 1 else '--'

        if member.guild_permissions.administrator:
            title = 'Guild Administrator'
        else:
            title = 'Guild Member'
        
        embed = discord.Embed(title=f'{member} ({member.nick})',
                              description=title)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name='ID', value=member.id, inline=False)
        embed.add_field(name='Joined Guild', value=join_str, inline=True)
        embed.add_field(name='Highest Role', value=highest_role, inline=True)
        embed.add_field(name='Other Roles', value=other_roles, inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['1984', 'del', 'delete'])
    async def purge(self, ctx, flag='-ref'):
        """
        Deletes referenced message or current channel.
        Requires Delete Messages permission to delete messages.
        Requires Manage Channels permission to delete channels.
        """
        msg = ctx.message
        
        if flag == '-ref':
            ref = msg.reference
            
            if ref and ref.message_id:
                target = await ctx.channel.fetch_message(ref.message_id)

                if await validate(ctx, 'manage_messages'):
                    await target.delete()

                    if ctx.guild:
                        await msg.delete()
            else:
                await ctx.message.add_reaction('\U0001F615')
                await ctx.send("No target provided.")
        elif flag == '-bulk':
            if await validate(ctx, 'manage_messages', guild_only=True):
                await ctx.channel.purge()
        elif flag == '-channel':
            if await validate(ctx, 'manage_channels', guild_only=True):
                await ctx.channel.delete()
        elif flag == '-vc':
            if await validate(ctx, 'manage_channels', guild_only=True):
                voice = ctx.author.voice

                if voice and voice.channel:
                    await voice.channel.delete()
                    await ctx.send("Deleted the voice channel.")
                else:
                    await msg.add_reaction('\U0001F615');
                    await ctx.send("You're not in a voice channel.")
        else:
            await msg.add_reaction('\U0001F615')
            await ctx.send("Unrecognized flag.")
    
    @commands.command(aliases=['','drag'])
    async def summon(self, ctx):
        """
        Moves tagged users to author's voice channel.

        Requires Move Members permission.
        """
        if not await validate(ctx, 'move_members', guild_only=True):
            return
        
        mentions = ctx.message.mentions
        voice = ctx.author.voice

        if not (voice and voice.channel):
            await ctx.message.add_reaction('\U0001F615')
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
                await ctx.message.add_reaction('\U0001F615')
                await ctx.send("No users were moved.")
            else:
                await ctx.message.add_reaction('\u26A0')
                await ctx.send("Some user(s) successfully moved. "
                               f"{skipped_msg(ctx, skipped)}.")
        elif len(ctx.message.content.split()) > 1:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("Unrecognized user mention(s).")
        else:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("No users mentioned.")

    @commands.command()
    async def undeafen(self, ctx):
        """
        Server undeafens user.

        Requires Deafen Members permission.
        """
        if not await validate(ctx, 'deafen_members', guild_only=True):
            return

        mentions = ctx.message.mentions
        
        if mentions:
            for user in mentions:
                await user.edit(deafen=False)

            await ctx.send("Server undeafened user(s).")
        else:
            await ctx.author.edit(deafen=False)
            await ctx.send(f"Server undeafened {ctx.author.mention}.")

    @commands.command()
    async def unmute(self, ctx):
        """
        Server unmutes user.

        Requires Mute Members permission.
        """
        if not await validate(ctx, 'mute_members', guild_only=True):
            return

        mentions = ctx.message.mentions
        
        if mentions:
            for user in mentions:
                await user.edit(mute=False)

            await ctx.send("Server unmuted user(s).")
        else:
            await ctx.author.edit(mute=False)
            await ctx.send(f"Server unmuted {ctx.author.mention}.")

    @commands.command()
    async def unpin(self, ctx):
        """
        Unpins referenced message.

        Requires Delete Messages permission.
        """
        if not await validate(ctx, 'manage_messages'):
            return
        
        ref = ctx.message.reference
        
        if ref and ref.message_id:
            target = await ctx.channel.fetch_message(ref.message_id)

            if target.pinned:
                await target.unpin()
                await ctx.send("Message unpinned.")
            else:
                await ctx.message.add_reaction('\U0001F615')
                await ctx.send("Message not pinned.")
        else:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send(f"No message referenced.")
    
def setup(bot):
    bot.add_cog(Mod(bot))
