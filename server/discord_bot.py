from discord.ext import commands
import discord, os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn
from pydantic import BaseModel

load_dotenv()

intents = discord.Intents.all()
app = FastAPI()
bot = commands.Bot(command_prefix='!', intents=intents)

# @app.post("/discord")
async def start_bot(message, discord_id):
    bot.run(os.getenv('TOKEN'))
    user = await bot.fetch_user(discord_id)
    await user.send(message)
    print('sent to ' , discord_id)
    await bot.close()
    return {"status": "success"}

# @app.on_event("startup")
# async def startup_event():
#     # Replace TOKEN with your bot's token
#     await bot.run(os.getenv('DISCORD_TOKEN'))

@app.on_event("shutdown")
async def shutdown_event():
    await bot.close()

# if __name__ == "__main__":
#     # uvicorn.run(app, port=8000)
#     bot.run(os.getenv('DISCORD_TOKEN'))
