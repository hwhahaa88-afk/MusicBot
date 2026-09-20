git add .
import discord
from discord.ext import commands
import asyncio
import random
import re
from ytmusicapi import YTMusic
from core import music_state

ytm = YTMusic()

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -b:a 320k'
}
VOICE_CHANNEL_ID = 1540686258379169814

def format_duration(seconds):
    if not seconds: return "00:00"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0: return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def get_isolated_stream(video_id):
    proxies = [
        "https://vid.puffyan.us",
        "https://inv.tux.pizza",
        "https://invidious.nerdvpn.de"
    ]
    return f"{random.choice(proxies)}/latest_version?id={video_id}&itag=140&local=true"

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.channel.id != 1540686258379169814: return
        content = message.content.strip()
        if not content: return
        parts = content.split('\n')[0].split(' ', 1)
        cmd = parts[0].lower()
        query = parts[1] if len(parts) > 1 else ""

        if cmd in ['play', 'p', 'ش', 'شغل', '1play', '1p', '1ش', '1شغل']:
            
            user_voice = message.author.voice
            if not user_voice or user_voice.channel.id != VOICE_CHANNEL_ID:
                try:
                    bot_msg = await message.reply(f"*You must be listening in Voice Room.*", mention_author=False)
                except: pass
                return

            if not query:
                try:
                    bot_msg = await message.reply("`1play [Song]` *: Play from **YouTube***\n`1play [URL]` : *Play from **YouTube/Spotify***", mention_author=False)
                except: pass
                return

            await self._play_logic(message, query)

    def play_next(self, message):
        guild = message.guild
        vc = guild.voice_client
        if not vc or not vc.is_connected(): return

        q = music_state.queues.setdefault(guild.id, [])
        is_looping = music_state.loops.get(guild.id, False)
        
        next_song = None
        if is_looping and guild.id in music_state.current_song:
            next_song = music_state.current_song[guild.id]
        elif len(q) > 0:
            next_song = q.pop(0)
            music_state.current_song[guild.id] = next_song
        else:
            music_state.current_song.pop(guild.id, None)

        if next_song:
            try:
                source = discord.FFmpegPCMAudio(next_song['url'], **FFMPEG_OPTIONS)
                current_vol = music_state.volumes.get(guild.id, 1.0)
                vol_source = discord.PCMVolumeTransformer(source, volume=current_vol)
                vc.play(vol_source, after=lambda e: self.bot.loop.call_soon_threadsafe(self.play_next, message))
            except Exception as e:
                self.bot.loop.call_soon_threadsafe(self.play_next, message)

    async def _play_logic(self, message, search):
        guild = message.guild
        vc = guild.voice_client

        if not vc or not vc.is_connected():
            channel = self.bot.get_channel(VOICE_CHANNEL_ID)
            if channel: vc = await channel.connect(self_deaf=True)
            else: return

        try:
            loop = asyncio.get_event_loop()
            def extract():
                is_url = search.startswith("http")
                video_id = None
                song_title = "Unknown Track"
                duration_sec = 0

                if not is_url:
                    try:
                        results = ytm.search(search, filter="songs", limit=1)
                        if not results:
                            results = ytm.search(search, limit=1)
                        if results:
                            video_id = results[0].get('videoId')
                            song_title = results[0].get('title', 'Unknown Track')
                            duration_sec = results[0].get('duration_seconds', 0)
                    except: pass
                else:
                    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', search)
                    if match:
                        video_id = match.group(1)

                if video_id:
                    return {
                        'title': song_title if not is_url else f"YouTube Video",
                        'url': get_isolated_stream(video_id),
                        'duration': duration_sec
                    }
                
                return "ERROR: Not Found"
            
            info = await loop.run_in_executor(None, extract)
            
            if isinstance(info, str) and info.startswith("ERROR:"):
                return

            if not info or 'url' not in info: 
                return
            
            song_data = {
                'title': info.get('title', 'Unknown Track'),
                'url': info['url'],
                'requester': message.author.display_name.upper(),
            }

            if vc.is_playing() or vc.is_paused():
                music_state.queues.setdefault(guild.id, []).append(song_data)
                try:
                    await message.reply(f"*Add song* : **{song_data['title']}** *by :* **{song_data['requester']}**.", mention_author=False)
                except: pass
            else:
                music_state.current_song[guild.id] = song_data
                try:
                    source = discord.FFmpegPCMAudio(song_data['url'], **FFMPEG_OPTIONS)
                    current_vol = music_state.volumes.get(guild.id, 1.0)
                    vol_source = discord.PCMVolumeTransformer(source, volume=current_vol)
                    
                    vc.play(vol_source, after=lambda e: self.bot.loop.call_soon_threadsafe(self.play_next, message))
                    
                    try:
                        await message.reply(f"*Playing song* : **{song_data['title']}** *by :* **{song_data['requester']}**.", mention_author=False)
                    except: pass
                except Exception as e:
                    pass
        except: pass

async def setup(bot):
    await bot.add_cog(Play(bot))
