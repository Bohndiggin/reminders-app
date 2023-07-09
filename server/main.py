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
    gmail_bot_main(request_data['subject'], request_data['message'], request_data['email'])
    return {"message": "success"}

@app.post("/discord")
async def start_bot(request: Request):
    request_data = await request.json()
    await message_ready(request_data['message'])
    await shutdown_event()
    return {"message": "success"}

async def message_ready(reminder_message):
    @bot.event
    async def on_ready():
        # with open('secrets.json', 'r') as f:
        #     secret_list = json.load(f)
        print(f'{bot.user} has connected to Discord!')
        # for i in secret_list["discord_IDs"]:
        target_user = os.getenv('TARGET_USER')
        user = await bot.fetch_user(target_user)
        time.sleep(1)
        await user.send(reminder_message)
        print('sent to ' , str(target_user))
        # await bot.close()

    await bot.start(os.getenv('DISCORD_TOKEN'))
    return {"message": "success"}

@app.on_event("shutdown")
async def shutdown_event():
    await bot.close()

# Need to rewrite the server to only add reminders and times to a database and then it'll tick forward and send reminders as needed.

@app.post('/reminder')
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
                (
                    '{reminder_name}', '{email}', '{frequency}', (current_date), '{target_time}', '{fuzziness}'
                );
    """.format(**request_data))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "reminder post sucsessful"}

@app.delete('/reminder')
async def delete_reminder(request: Request):
    request_data = await request.json()
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
    except Exception as e:
        print(e)
    try:
        cur.execute("""
            DELETE FROM Reminders WHERE id = {id};
        """.format(**request_data))
        conn.commit()
        cur.close()
        conn.close()
        return {"message": "Deletion Sucessful of {id}".format(**request_data)}
    except Exception as e:
        print('Deletion Error', e)
        cur.close()
        conn.close()
        return {"message": "Deletion NOT Sucessful of {id}, for reason ".format(**request_data), "error": e}
