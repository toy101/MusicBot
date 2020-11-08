import discord
from discord.ext import commands
import os
import traceback

from ytdl import YTDLSource

bot = commands.Bot(command_prefix='/')

token_path = "token.txt"
try:
    # For local test
    with open(token_path) as f:
        TOKEN = f.read()
        TOKEN = TOKEN.strip()
except:
    # For deploy on Heroku
    TOKEN = os.environ['DISCORD_BOT_TOKEN']
    # if not discord.opus.is_loaded():
    #     discord.opus.load_opus("heroku-buildpack-libopus")

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["connect","summon"]) #connectやsummonでも呼び出せる
    async def join(self, ctx):
        """Botをボイスチャンネルに入室させます。"""
        voice_state = ctx.author.voice

        if (not voice_state) or (not voice_state.channel):
            await ctx.send("先にボイスチャンネルに入っている必要があります。")
            return

        channel = voice_state.channel

        await channel.connect()
        print("connected to:",channel.name)

    @commands.command(aliases=["disconnect", "bye", "kill"])
    async def stop(self, ctx):
        """Botをボイスチャンネルから切断します。"""
        voice_client = ctx.message.guild.voice_client

        if not voice_client:
            await ctx.send("Botはこのサーバーのボイスチャンネルに参加していません。")
            return

        await voice_client.disconnect()
        await ctx.send("ボイスチャンネルから切断しました。")

    # @commands.command()
    # async def play(self, ctx, *, query):
    #     """Plays a file from the local filesystem"""
    #
    #     source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
    #     ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
    #
    #     await ctx.send('Now playing: {}'.format(query))
    #
    @commands.command(aliases=["p"])
    async def play(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                                                            # if stream=False
                                                            # do predownload
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)


#
#
# @bot.command(aliases=["disconnect","bye"])
# async def leave(ctx):
#     """Botをボイスチャンネルから切断します。"""
#     voice_client = ctx.message.guild.voice_client
#
#     if not voice_client:
#         await ctx.send("Botはこのサーバーのボイスチャンネルに参加していません。")
#         return
#
#     await voice_client.disconnect()
#     await ctx.send("ボイスチャンネルから切断しました。")
#

# @bot.command()
# async def play(ctx):
#     """指定された音声ファイルを流します。"""
#     voice_client = ctx.message.guild.voice_client
#
#     if not voice_client:
#         await ctx.send("Botはこのサーバーのボイスチャンネルに参加していません。")
#         return
#
#     if not ctx.message.attachments:
#         await ctx.send("ファイルが添付されていません。")
#         return
#
#     await ctx.message.attachments[0].save("tmp.mp3")
#
#     ffmpeg_audio_source = discord.FFmpegPCMAudio("tmp.mp3")
#     voice_client.play(ffmpeg_audio_source)
#
#     await ctx.send("再生しました。")

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

bot.add_cog(Music(bot))
bot.run(TOKEN)
