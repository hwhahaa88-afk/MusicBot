import discord
from discord.ext import commands
from core import music_state

VOICE_CHANNEL_ID = 1540686258379169814

class Skip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.channel.id != 1540686258379169814: return
        cmd = message.content.strip().split('\n')[0].split(' ', 1)[0].lower()

        if cmd in ['skip', 's', 'سكب', 'س']:
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

            vc = message.guild.voice_client
            if vc and vc.is_playing():
                music_state.loops[message.guild.id] = False
                current_song = music_state.current_song.get(message.guild.id)
                title = current_song['title'] if current_song else "Unknown Track"
                requester = current_song['requester'] if current_song else "UNKNOWN"
                
                vc.stop()
                try:
                    bot_msg = await message.reply(f"*Skiped :* **{title}** *by :* **{requester}**.", mention_author=False)
                    music_state.bot_replies[message.id] = bot_msg
                except: pass
            else:
                try:
                    bot_msg = await message.reply("*Server queue is empty.*", mention_author=False)
                    music_state.bot_replies[message.id] = bot_msg
                except: pass

async def setup(bot):
    await bot.add_cog(Skip(bot))
