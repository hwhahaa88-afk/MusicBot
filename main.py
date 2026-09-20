import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    
    # وضع حالة البوت إلى Streaming باسم Rouse
    activity = discord.Streaming(name="Rouse", url="https://www.twitch.tv/discord")
    await bot.change_presence(activity=activity)
    
    channel = bot.get_channel(1540686258379169814)
    if channel:
        try:
            # الدخول للروم تلقائياً أول ما يشتغل وهو مسوي دفن
            await channel.connect(self_deaf=True)
        except: pass

async def main():
    await load_cogs()
    await bot.start("YOUR_TOKEN")

asyncio.run(main())
