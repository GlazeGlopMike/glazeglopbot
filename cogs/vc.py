# vc.py
import discord
import os

from discord.ext import commands

class VC(commands.Cog):
    """Cog wrapping voice channel commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['connect'])
    async def join(self, ctx):
        """Joins author's voice channel."""
        voice = ctx.author.voice

        if not (voice and voice.channel):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("You're not in a voice channel.")
        else:
            await voice.channel.connect()
    
    @commands.command()
    async def leave(self, ctx):
        """Disconnects bot from its voice channel."""
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
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

    @commands.command()
    async def screech(self, ctx):
        """
        Plays 'REE' sound.

        Joins the author's voice channel if not in one.
        Interrupts the current sound if necessary.
        """
        await self.sound(ctx, 'ree')

    @commands.command(aliases=['snd'])
    async def sound(self, ctx, name='default', start=0):
        """
        Plays a local sound from the specified timestamp in seconds.
        Searches for sounds in sounds/[name].ogg

        Joins the author's voice channel if not in one.
        Interrupts the current sound if necessary.
        Default sound is 'sounds/default.ogg'.
        """
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        if not voice:
            await self.join(ctx)
        
        ffmpeg_path = os.getenv('FFMPEG_PATH')
        sound_path = f'sounds/{name}.ogg'
        ffmpeg_opts = {'options': f'-ss {start}'}

        if not os.path.isfile(sound_path):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("Sound file not found.")
            return
        
        audio = discord.FFmpegPCMAudio(executable=ffmpeg_path,
                                       source=sound_path, **ffmpeg_opts)
        sound = discord.PCMVolumeTransformer(audio)
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if voice:
            if voice.is_playing():
                voice.stop()
        
        ctx.voice_client.play(sound)
        await ctx.send(f"Playing '{name}.ogg.'")

    @sound.error
    async def sound_err(self, ctx, err):
        if isinstance(err, commands.error.BadArgument):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send(f"Unrecognized timestamp.")

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
    
    async def cog_check(self, ctx):
        return bool(ctx.guild)

    async def cog_command_error(self, ctx, err):
        if isinstance(err, commands.errors.CheckFailure):
            await ctx.message.add_reaction('\U0001F615')
            await ctx.send("Not in a guild.")

def setup(bot):
    bot.add_cog(VC(bot))
