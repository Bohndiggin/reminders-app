from discord.ext import commands
import discord
from gmail_reminder_server import *
import os, json
from dotenv import load_dotenv
import datetime, time
from fastapi import FastAPI, Request
# from pydantic import BaseModel
load_dotenv()

app = FastAPI()
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

# def main():
#     pass

# if __name__ == '__main__':
#     main()

# class ReminderMessage(BaseModel):
#     message: str

# message = ReminderMessage('')

@app.get('/')
async def root():
    return {"message": "Hello World"}

@app.post('/gmail')
async def gmail_run(request: Request):
    request_data = await request.json()
    gmail_bot_main(request_data['subject'], request_data['message'])
    return {"message": "success"}

@app.post("/discord")
async def start_bot(request: Request):
    request_data = await request.json()
    await message_ready(request_data['message'])
    return {"message": "success"}

async def message_ready(reminder_message):
    @bot.event
    async def on_ready():
        with open('secrets.json', 'r') as f:
            secret_list = json.load(f)
        print(f'{bot.user} has connected to Discord!')
        for i in secret_list["discord_IDs"]:
                user = await bot.fetch_user(i)
                time.sleep(1)
                await user.send(reminder_message)
                print('sent to ' + str(i))
        await bot.close()

    await bot.start(os.getenv('DISCORD_TOKEN'))

@app.on_event("shutdown")
async def shutdown_event():
    await bot.close()
