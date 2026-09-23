import discord
from discord.ext import commands
import asyncio
import os
from aiohttp import web

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"✅ Web server listening on port {port}")

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
    if not os.path.exists('./cogs'):
        return
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try: await bot.load_extension(f'cogs.{filename[:-3]}')
            except: pass

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    activity = discord.Streaming(name="Music", url="https://twitch.tv/discord")
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
                print("✅ متصل بالروم")
            except Exception: pass

@bot.event
async def on_voice_state_update(member, before, after):
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
    await start_web_server()
    await load_cogs()
    token = os.getenv("DISCORD_TOKEN")
    if token:
        await bot.start(token)
    else:
        print("Waiting for token...")

if __name__ == "__main__":
    try: asyncio.run(main())
    except: pass
