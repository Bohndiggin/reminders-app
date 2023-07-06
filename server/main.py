from discord.ext import commands
import discord
from gmail_reminder_server import *
import os, json
from dotenv import load_dotenv
import datetime, time
from fastapi import FastAPI, Request
import psycopg2

load_dotenv()

app = FastAPI()
intents = discord.Intents.all()
db_url = os.getenv("DB_API")
bot = commands.Bot(command_prefix='!', intents=intents)


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

# Need to rewrite the server to only add reminders and times to a database and then it'll tick forward and send reminders as needed.

@app.post('/add_reminder')
async def insert_reminder(request: Request):
    request_data = await request.json()
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
    except Exception as e:
        print(e)
    cur.execute("""
        INSERT INTO Reminders(reminder_name, email, frequency, date_made, target_time, fuzziness)
        VALUES
                ('{reminder_name}', '{email}', '{frequency}', '{date_made}', '{target_time}', '{fuzziness}'
                );
    """.format(**request_data))
    conn.commit()
    cur.close()
    conn.close()
