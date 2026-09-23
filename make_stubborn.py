import re

with open('main.py', 'r') as f:
    content = f.read()

token_match = re.search(r'bot\.start\([\'"]([^\'"]+)[\'"]\)', content)
token = token_match.group(1) if token_match else "YOUR_TOKEN"

main_code = f"""import discord
from discord.ext import commands
import asyncio
import os

if not discord.opus.is_loaded():
    try: discord.opus.load_opus('libopus.so')
    except: 
        try: discord.opus.load_opus('/data/data/com.termux/files/usr/lib/libopus.so')
        except: pass

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

TARGET_VC = 1540686258379169814

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try: await bot.load_extension(f'cogs.{{filename[:-3]}}')
            except: pass

@bot.event
async def on_ready():
    print(f"Logged in as {{bot.user.name}}")
    activity = discord.Streaming(name="Rouse", url="https://www.twitch.tv/discord")
    await bot.change_presence(activity=activity)
    bot.loop.create_task(stubborn_connect())

async def stubborn_connect():
    await bot.wait_until_ready()
    channel = bot.get_channel(TARGET_VC)
    if channel:
        guild = channel.guild
        vc = guild.voice_client
        if not vc or not vc.is_connected():
            try:
                await channel.connect(self_deaf=True)
                print("✅ دخلت الروم بنجاح ولن أخرج منه!")
            except Exception as e:
                print(f"❌ خطأ في دخول الروم: {{e}}")

@bot.event
async def on_voice_state_update(member, before, after):
    # نظام العناد: إذا انطرد أو انسحب يرجع فوراً
    if member.id == bot.user.id:
        if after.channel is None:
            await asyncio.sleep(1)
            await stubborn_connect()
        elif after.channel.id != TARGET_VC:
            guild = after.channel.guild
            vc = guild.voice_client
            if vc: await vc.disconnect()
            await asyncio.sleep(1)
            await stubborn_connect()

async def main():
    await load_cogs()
    await bot.start("{token}")

if __name__ == "__main__":
    try: asyncio.run(main())
    except: pass
"""
with open('main.py', 'w') as f:
    f.write(main_code)

print("✅ تم تعديل الملف الأساسي ليكون البوت عنيداً!")
