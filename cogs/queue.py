import discord
from discord.ext import commands
from core import music_state

VOICE_CHANNEL_ID = 1540686258379169814

class Queue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.channel.id != 1540686258379169814: return
        cmd = message.content.strip().split('\n')[0].split(' ', 1)[0].lower()

        if cmd in ['queue', 'q', 'قائمه', 'قائمة']:
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
            current = music_state.current_song.get(message.guild.id)
            
            if not vc or not current:
                try:
                    bot_msg = await message.reply("*Server queue is empty.*", mention_author=False)
                    music_state.bot_replies[message.id] = bot_msg
                except: pass
                return

            q = music_state.queues.get(message.guild.id, [])
            total_songs = len(q) + 1
            
            dur = current.get('duration', '00:00')
            desc = f"*Total songs :* **({total_songs})**\n"
            desc += f"*Now playing :*\n"
            desc += f"**{current['title']} ({dur})** *by :*\n**{current['requester']}**\n\n"
            
            for i, s in enumerate(q[:10]):
                sdur = s.get('duration', '00:00')
                desc += f"**{i+1}. {s['title']} ({sdur})** *by :* **{s['requester']}**\n"

            embed = discord.Embed(description=desc, color=0xEAEAEA)
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/727/727218.png")
            
            total_pages = (len(q) // 10) + 1 if len(q) > 0 else 1
            embed.set_footer(text=f"Page 1/{total_pages}")
            
            try:
                bot_msg = await message.reply(embed=embed, mention_author=False)
                music_state.bot_replies[message.id] = bot_msg
            except: pass

async def setup(bot):
    await bot.add_cog(Queue(bot))
