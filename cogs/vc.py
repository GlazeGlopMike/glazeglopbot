# vc.py
import os
import discord
import youtube_dl

from discord.ext import commands

class VC(commands.Cog):
    """Cog wrapping voice channel commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['connect'])
    async def join(self, ctx):
        """Joins author's voice channel."""
        voice = ctx.author.voice

        if voice and voice.channel:
            channel = voice.channel
            
            try:
                await channel.connect()
            except discord.errors.ClientException:
                await ctx.guild.get_member(self.bot.user.id).move_to(channel)   
            
            await ctx.send(f"Joined `{channel.name}`.")
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("You're not in a voice channel.")
    
    @commands.command()
    async def leave(self, ctx):
        """Disconnects bot from its voice channel."""
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
            await ctx.send("Left voice channel.")
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("Not in a voice channel.")

    @commands.command()
    async def pause(self, ctx):
        """Pauses currently playing sound."""
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if voice:
            if voice.is_playing():
                voice.pause()
                await ctx.send("Playing paused.")
            else:
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("Not playing anything right now.")
        else:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("Not in a voice channel.")

    @commands.command(aliases=['unpause'])
    async def resume(self, ctx):
        """Resumes currently playing sound."""
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if voice:
            if voice.is_paused():
                voice.resume()
                await ctx.send("Playing resumed.")
            else:
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("Nothing paused right now.")
        else:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("Not in a voice channel.")

    @commands.command(aliases=['snd'])
    async def sound(self, ctx, name='default', start=0):
        """
        Plays local sound from timestamp in seconds.
        Searches for sound 'sounds/[name].ogg'.

        Joins author's voice channel if not in one.
        Interrupts current sound if necessary.
        Default sound is 'sounds/default.ogg'.
        Starts at beginning by default.
        """
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        if not (ctx.author.voice or voice):
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("Not in a voice channel.")
            return
        
        ffmpeg_path = os.environ['FFMPEG_PATH']
        sound_path = f'sounds/{name}.ogg'
        ffmpeg_opts = {'options': f'-ss {start}'}

        if not os.path.isfile(sound_path):
            if name == 'default':
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("No sound specified.")
            else:
                await ctx.message.add_reaction('\U0001F615');
                await ctx.send("Sound file not found.")
            return
        
        audio = discord.FFmpegPCMAudio(executable=ffmpeg_path,
                                       source=sound_path, **ffmpeg_opts)
        sound = discord.PCMVolumeTransformer(audio)
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        if not voice:
            await self.join(ctx)

        if voice:
            if voice.is_playing():
                voice.stop()
        
        voice.play(sound)
        await ctx.send(f"Playing `{name}.ogg`.")

    @sound.error
    async def sound_err(self, ctx, err):
        if isinstance(err, commands.errors.BadArgument):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"Invalid timestamp.")

    @commands.command()
    async def stop(self, ctx):
        """Stops currently playing sound."""
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if voice:
            if voice.is_playing():
                voice.stop()
                await ctx.send("Playing stopped.") 
            else:
                await ctx.message.add_reaction('\U0001F615')
                await ctx.send("Not playing anything right now.")
        else:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("Not in a voice channel.")

    @commands.command(aliases=['vol'])
    async def volume(self, ctx, level:int):
        """Adjusts volume of current sound."""
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if voice:
            if voice.is_playing():
                if 0 <= level <= 200:
                    voice.source.volume = level / 100
                    await ctx.send(f"Adjusted volume to {level}%.")
            else:
                await ctx.message.add_reaction('\U0001F615')
                await ctx.send("Not playing anything right now.")
        else:
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("Not in a voice channel.")

    @volume.error
    async def volume_err(self, ctx, err):
        if isinstance(err, commands.errors.BadArgument):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("Need a level between 0 and 200.")
        elif isinstance(err, commands.errors.MissingRequiredArgument):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("No volume specified.")

    @commands.command(aliases=['yt'])
    async def youtube(self, ctx, *url):
        """
        Plays YouTube video from URL.

        Joins author's voice channel if not in one.
        Interrupts current sound if necessary.
        """
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if not (ctx.author.voice or voice):
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("Not in a voice channel.")
            return
        
        YDL_OPTS = {'format': 'bestaudio', 'noplaylist': 'True'}
        FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 '
                       '-reconnect_delay_max 5',
                       'options': '-vn'}
        
        with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
            info = (ydl.extract_info(f'ytsearch:{url}', download=False)
                    ['entries'][0])
        
        if not voice:
            await self.join(ctx)

        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        if voice:
            if voice.is_playing():
                voice.stop()
        
        URL = info['formats'][0]['url']
        title = info['title']
        voice.play(discord.FFmpegPCMAudio(executable=os.environ['FFMPEG_PATH'],
                                          source=URL, **FFMPEG_OPTS))
        
        await ctx.send(f"Playing `{title}`.")

    @youtube.error
    async def yt_err(self, ctx, err):
        if isinstance(err, commands.errors.MissingRequiredArgument):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"No URL provided.")
        elif isinstance(err, youtube_dl.utils.DownloadError):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"Couldn't download the video.")
    
    async def cog_check(self, ctx):
        return bool(ctx.guild)
        
    async def cog_command_error(self, ctx, err):
        if isinstance(err, commands.errors.CheckFailure):
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("Not in a guild.")
        elif (isinstance(err, commands.ConversionError)
                and isinstance(err.original, discord.errors.ClientException)):
            await ctx.message.add_reaction('\U0001F916')
            await ctx.send("Couldn't play sound due to missing dependency.")
        else:
            print(err)

def setup(bot):
    bot.add_cog(VC(bot))
