import discord
from discord.ext import commands
from core import music_state

VOICE_CHANNEL_ID = 1540686258379169814

class Loop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.channel.id != 1540686258379169814: return
        cmd = message.content.strip().split('\n')[0].split(' ', 1)[0].lower()

        if cmd in ['loop', 'lp', 'تكرار', 'ت']:
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

            current_state = music_state.loops.get(message.guild.id, False)
            new_state = not current_state
            music_state.loops[message.guild.id] = new_state

            state_text = "ON" if new_state else "OFF"
            try:
                bot_msg = await message.reply(f"*Loop mode is* **{state_text}**", mention_author=False)
                music_state.bot_replies[message.id] = bot_msg
            except: pass

async def setup(bot):
    await bot.add_cog(Loop(bot))
