import discord
from discord.ext import commands
import asyncio
import yt_dlp
from core import music_state

TARGET_VC = 1540686258379169814

# إعدادات صلبة وثابتة لمنع أخطاء الـ Broken pipe والاتصال
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10 -analyzeduration 0',
    'options': '-vn -b:a 128k'
}

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch1',
    'source_address': '0.0.0.0',
    'socket_timeout': 15,
}
ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

if not discord.opus.is_loaded():
    try: discord.opus.load_opus('libopus.so')
    except: pass

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        content = message.content.strip()
        if not content: return
        parts = content.split('\n')[0].split(' ', 1)
        cmd = parts[0].lower()
        
        clean_cmd = cmd
        if clean_cmd.startswith('!'): clean_cmd = clean_cmd[1:]
        
        valid_cmds = ['play', 'p', 'ش', 'شغل', '1play', '1p', '1ش', '1شغل']
        
        if clean_cmd in valid_cmds or cmd in valid_cmds:
            
            guild = message.guild
            bot_vc = guild.voice_client
            user_voice = message.author.voice
            
            if not user_voice or not user_voice.channel:
                try: await message.reply("*You must be in a Voice Channel first.*", mention_author=False)
                except: pass
                return
            
            if user_voice.self_deaf or user_voice.deaf:
                try: await message.reply("*You must undeafen to use this command.*", mention_author=False)
                except: pass
                return

            if bot_vc and bot_vc.is_connected():
                if user_voice.channel.id != bot_vc.channel.id:
                    try: await message.reply(f"*You must be listening in* **`{bot_vc.channel.name}`**.", mention_author=False)
                    except: pass
                    return

            query = parts[1].strip() if len(parts) > 1 else ""
            
            if not query:
                try: 
                    await message.reply("`1play [Song]` *: Play from **YouTube***\n`1play [URL]` : *Play from **SoundCloud/Spotify***", mention_author=False)
                except: pass
                return
                
            asyncio.create_task(self._play_logic(message, query))

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
            except:
                self.bot.loop.call_soon_threadsafe(self.play_next, message)

    async def _play_logic(self, message, search):
        guild = message.guild
        vc = guild.voice_client

        if not vc or not vc.is_connected():
            target_channel = guild.get_channel(TARGET_VC)
            if target_channel:
                try: vc = await target_channel.connect(self_deaf=True)
                except Exception as e:
                    if "Already connected" in str(e): vc = guild.voice_client
                    else: return

        try:
            loop = asyncio.get_event_loop()
            search_query = f"ytsearch1:{search}" if not search.startswith("http") else search
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search_query, download=False))
            
            if 'entries' in data: data = data['entries'][0]
            song_data = {
                'title': data.get('title', 'Unknown Track'),
                'url': data.get('url'),
                'requester': message.author.display_name,
            }

            if vc.is_playing() or vc.is_paused():
                music_state.queues.setdefault(guild.id, []).append(song_data)
                try: await message.reply(f"*Add song :* **{song_data['title']}** *by :* **{song_data['requester']}**.", mention_author=False)
                except: pass
            else:
                music_state.current_song[guild.id] = song_data
                try:
                    source = discord.FFmpegPCMAudio(song_data['url'], **FFMPEG_OPTIONS)
                    current_vol = music_state.volumes.get(guild.id, 1.0)
                    vol_source = discord.PCMVolumeTransformer(source, volume=current_vol)
                    vc.play(vol_source, after=lambda e: self.bot.loop.call_soon_threadsafe(self.play_next, message))
                    try: await message.reply(f"*Playing song :* **{song_data['title']}** *by :* **{song_data['requester']}**.", mention_author=False)
                    except: pass
                except Exception as e:
                    pass
        except Exception as e:
            pass

async def setup(bot):
    await bot.add_cog(Play(bot))
