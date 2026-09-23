import discord
from discord.ext import commands
import asyncio
import yt_dlp

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'extract_flat': False
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def execute_play(self, ctx_or_message, search: str):
        if not search:
            return

        author = ctx_or_message.author
        guild = ctx_or_message.guild
        channel = ctx_or_message.channel

        if not author.voice:
            await channel.send("❌ ادخل روم صوتي أولاً!", delete_after=5)
            return

        vc = guild.voice_client
        if not vc:
            try:
                vc = await author.voice.channel.connect()
            except Exception:
                pass

        # استجابة فائقة السرعة 0.3 ثانية
        await asyncio.sleep(0.3)

        msg = await channel.send("🔍 جاري التشغيل...")

        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=False))
            if 'entries' in data:
                data = data['entries'][0]

            url = data['url']
            title = data.get('title', 'مقطع صوتي')

            if vc and vc.is_playing():
                vc.stop()

            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            vc.play(source)

            await msg.edit(content=f"🎶 **شغال الآن:** {title}")
        except Exception as e:
            await msg.edit(content=f"❌ تعذر تشغيل المقطع: {e}")

    # أمر مع البادئة (!1play)
    @commands.command(name="1play")
    async def play_prefix(self, ctx, *, search: str = None):
        if not search:
            await ctx.send("❌ اكتب اسم أو رابط المقطع بعد الأمر!", delete_after=5)
            return
        await self.execute_play(ctx, search)

    # تشغيل بدون بادئة (Prefix-less) للأوامر: play, p, شغل, ش
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        content = message.content.strip()
        parts = content.split(" ", 1)
        trigger = parts[0].lower()

        prefixless_commands = ["play", "p", "شغل", "ش"]

        if trigger in prefixless_commands:
            if len(parts) > 1:
                search_query = parts[1].strip()
                await self.execute_play(message, search_query)
            else:
                await message.channel.send("❌ اكتب اسم أو رابط المقطع!", delete_after=5)

async def setup(bot):
    await bot.add_cog(Play(bot))
