import discord
from discord.ext import commands
from core import music_state

VOICE_CHANNEL_ID = 1540686258379169814

class Volume(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.channel.id != 1540686258379169814: return
        parts = message.content.strip().split('\n')[0].split(' ', 1)
        cmd = parts[0].lower()

        if cmd in ['volume', 'v', 'صوت', 'ص']:
            if len(parts) < 2: return

            user_voice = message.author.voice
            if not user_voice or user_voice.channel.id != VOICE_CHANNEL_ID:
                target_vc = self.bot.get_channel(VOICE_CHANNEL_ID)
                vc_name = target_vc.name if target_vc else "Voice Room"
                try:
                    bot_msg = await message.reply(f"*You must be listening in* **``{vc_name}``**.", mention_author=False)
                    music_state.bot_replies[message.id] = bot_msg
                except: pass
                return

            if user_voice.self_deaf or user_voice.deaf:
                try:
                    bot_msg = await message.reply("*You must to unDeafen to use commands .*", mention_author=False)
                    music_state.bot_replies[message.id] = bot_msg
                except: pass
                return

            try:
                new_vol_num = int(parts[1])
                
                if new_vol_num < 0 or new_vol_num > 150:
                    try:
                        bot_msg = await message.reply("*The volume must be between **0-150**.*", mention_author=False)
                        music_state.bot_replies[message.id] = bot_msg
                    except: pass
                    return

                old_vol = music_state.volumes.get(message.guild.id, 1.0)
                new_vol = float(new_vol_num) / 100.0
                
                vc = message.guild.voice_client
                if vc and hasattr(vc.source, 'volume'):
                    vc.source.volume = new_vol
                    music_state.volumes[message.guild.id] = new_vol
                    
                    old_vol_num = int(old_vol * 100)
                    try:
                        bot_msg = await message.reply(f"*Volume changed from* ``{old_vol_num}%`` *to* ``{new_vol_num}%`` .", mention_author=False)
                        music_state.bot_replies[message.id] = bot_msg
                    except: pass
            except ValueError:
                pass

async def setup(bot):
    await bot.add_cog(Volume(bot))
