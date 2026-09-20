import discord
from discord.ext import commands
import asyncio
from core import music_state

VOICE_CHANNEL_ID = 1540686258379169814

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if payload.message_id in music_state.bot_replies:
            try:
                bot_msg = music_state.bot_replies[payload.message_id]
                await bot_msg.delete()
            except: pass
            del music_state.bot_replies[payload.message_id]

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # التأكد أن التغيير يخص البوت فقط
        if member.id != self.bot.user.id:
            return

        # 1. نظام Anti-Disconnect (صاروخي)
        if before.channel and not after.channel:
            guild = member.guild
            if guild.voice_client:
                try:
                    await guild.voice_client.disconnect(force=True)
                except: pass
                
            # تم تقليل الانتظار من 2 ثانية إلى 0.1 ثانية فقط (أسرع شيء ممكن عشان ما يعلق الديسكورد)
            await asyncio.sleep(0.1)
            target_vc = self.bot.get_channel(VOICE_CHANNEL_ID)
            if target_vc:
                try:
                    await target_vc.connect(self_deaf=True)
                except: pass
            return 

        # 2. نظام Anti-Mute & Anti-Undeafen (فوري)
        if after.channel:
            updates = {}
            if after.mute:
                updates['mute'] = False
            if not after.deaf:
                updates['deafen'] = True
                
            if updates:
                try:
                    # التنفيذ في أجزاء من الثانية
                    await member.edit(**updates)
                except: pass

async def setup(bot):
    await bot.add_cog(Events(bot))
