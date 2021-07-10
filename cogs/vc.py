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
        """Joins the author's voice channel."""
        voice = ctx.author.voice

        if not (voice and voice.channel):
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("You're not in a voice channel.")
        else:
            await voice.channel.connect()
    
    @commands.command()
    async def leave(self, ctx):
        """Disconnects the bot from its voice channel."""
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.message.add_reaction('\U0001F615');
            await ctx.send("Not in a voice channel.")

    @commands.command()
    async def pause(self, ctx):
        """Pauses the currently playing sound."""
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
        """Resumes the currently playing sound."""
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
    async def stop(self, ctx):
        """Stops the currently playing sound."""
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

    @commands.command()
    async def screech(self, ctx):
        """
        Plays the REE sound in the current voice channel.

        Joins the author's voice channel if not already present.
        Interrupts the current sound if necessary.
        """
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        if not voice:
            await self.join(ctx)

        ffmpeg_path = os.getenv('FFMPEG_PATH')
        audio = discord.FFmpegPCMAudio(executable=ffmpeg_path,
                                       source='sounds/ree.mp3')
        sound = discord.PCMVolumeTransformer(audio)
        
        if voice.is_playing():
            voice.stop()
        
        ctx.voice_client.play(sound)
    
def setup(bot):
    bot.add_cog(VC(bot))
