from discord.ext import commands
from dotenv import load_dotenv
import discord, os, datetime
from pydantic import BaseModel

load_dotenv()

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(bot))
    user = await bot.fetch_user(os.getenv('OWNER_DISCORD'))
    await user.send(f'BOT ONLINE @{datetime.datetime.now()}')

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.mention}!')

@bot.command(name='delay')
async def hello(ctx):
    await ctx.send(f'Delaying task!')

class DiscordItem(BaseModel):
    subject: str
    message: str
    email: str | None
    discord_id: int

async def send_reminder_discord(discord_item: DiscordItem):
    user = await bot.fetch_user(discord_item.discord_id)
    await user.send(discord_item.message)
    # print('sent to ' , discord_item.discord_id)
    # await bot.close()
    return {"status": "success"}