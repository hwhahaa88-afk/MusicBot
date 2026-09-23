import discord
from discord.ext import commands
from core import music_state

# نفس إعدادات السرعة الصاروخية حقت التشغيل
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -analyzeduration 0',
    'options': '-vn -b:a 128k -threads 2'
}

class Seek(commands.Cog):
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
        
        # الاختصارات اللي طلبتيها
        valid_cmds = ['seek', 'قدم', 'ق', '1seek', '1قدم', '1ق']
        
        if clean_cmd in valid_cmds or cmd in valid_cmds:
            
            guild = message.guild
            vc = guild.voice_client
            user_voice = message.author.voice
            
            # التأكد من الشروط بصمت (بدون رد)
            if not user_voice or not user_voice.channel: return
            if user_voice.self_deaf or user_voice.deaf: return
            if not vc or not vc.is_playing(): return
            if user_voice.channel.id != vc.channel.id: return
            
            # التأكد أنك كتبتي وقت للتقديم
            if len(parts) < 2: return
            time_str = parts[1].strip()
            
            # تحويل الوقت (مثلاً 1:30 أو 90 ثانية) إلى ثواني
            seconds = 0
            try:
                if ':' in time_str:
                    t_parts = time_str.split(':')
                    if len(t_parts) == 2:
                        seconds = int(t_parts[0]) * 60 + int(t_parts[1])
                    elif len(t_parts) == 3:
                        seconds = int(t_parts[0]) * 3600 + int(t_parts[1]) * 60 + int(t_parts[2])
                else:
                    seconds = int(time_str)
            except:
                return
                
            current_song = music_state.current_song.get(guild.id)
            if not current_song: return
            
            try:
                # تطبيق التقديم على ملف الصوت
                new_before_options = f"-ss {seconds} " + FFMPEG_OPTIONS['before_options']
                new_source = discord.FFmpegPCMAudio(current_song['url'], before_options=new_before_options, options=FFMPEG_OPTIONS['options'])
                current_vol = music_state.volumes.get(guild.id, 1.0)
                vol_source = discord.PCMVolumeTransformer(new_source, volume=current_vol)
                
                # استبدال الصوت بالخلفية بدون إيقاف الطابور
                vc.pause()
                vc.source = vol_source
                vc.resume()
                
                # التفاعل بعلامة الصح فقط بدون رسالة
                await message.add_reaction("✅")
            except Exception as e:
                pass

async def setup(bot):
    await bot.add_cog(Seek(bot))
