from discord.ext import commands
import discord, os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn

load_dotenv()

intents = discord.Intents.all()
app = FastAPI()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@app.post("/discord")
async def start_bot(request: Request):
    request_data = await request.json()
    # background_tasks.add_task(message_ready, request_data['message'])
    target_user = os.getenv('TARGET_USER')
    user = await bot.fetch_user(target_user)
    await user.send(request_data['message'])
    print('sent to ' , target_user)
    return {"status": "success"}

# @app.on_event("startup")
# async def startup_event():
#     # Replace TOKEN with your bot's token
#     await bot.run(os.getenv('DISCORD_TOKEN'))

@app.on_event("shutdown")
async def shutdown_event():
    await bot.close()

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))
    uvicorn.run(app, port=8000)
