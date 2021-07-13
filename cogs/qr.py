# rng.py
import os
import uuid
import discord
import pyqrcode

from discord.ext import commands

class QR(commands.Cog):
    """Cog wrapping QR code generation commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['qr','qrgen'])
    async def makeqr(self, ctx, *, content='sample text'):
        """
        Sends a QR code image version of the input.

        Default QR code says "sample text".
        """
        # create the QR code
        qr = pyqrcode.create(content)

        # save temporary image
        path = str(uuid.uuid4().hex) + '.png'
        qr.png(path, scale = 16)

        # send image and delete temporary file
        await ctx.send(file=discord.File(path))
        os.remove(path)
        
    
def setup(bot):
    bot.add_cog(QR(bot))
