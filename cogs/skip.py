import discord
from discord.ext import commands
import asyncio
from core import music_state

class Skip(commands.Cog):
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
        
        valid_cmds = ['skip', 's', 'تخطي', '1skip', '1s']
        
        if clean_cmd in valid_cmds or cmd in valid_cmds:
            
            guild = message.guild
            vc = guild.voice_client
            user_voice = message.author.voice
            
            if not user_voice or not user_voice.channel:
                try: await message.reply("*You must be in a Voice Channel first.*", mention_author=False)
                except: pass
                return
            
            if user_voice.self_deaf or user_voice.deaf:
                try: await message.reply("*You must undeafen to use this command.*", mention_author=False)
                except: pass
                return

            if vc and vc.is_connected():
                if user_voice.channel.id != vc.channel.id:
                    try: await message.reply(f"*You must be listening in* **`{vc.channel.name}`**.", mention_author=False)
                    except: pass
                    return
                    
            if not vc or not vc.is_playing():
                try: await message.reply("*There is no song currently playing.*", mention_author=False)
                except: pass
                return

            # سحب اسم الأغنية الحالية قبل التخطي
            current = music_state.current_song.get(guild.id)
            title = current['title'] if current else "Unknown Track"
            skipper = message.author.display_name

            # تنفيذ الإيقاف وإرسال الرسالة كـ "مهمة خلفية" لسرعة استجابة فورية (0 تأخير)
            async def instant_skip():
                vc.stop()
                try: 
                    await message.reply(f"*Skiped :* **{title}** *by :* **{skipper}**.", mention_author=False)
                except: pass

            asyncio.create_task(instant_skip())

async def setup(bot):
    await bot.add_cog(Skip(bot))
