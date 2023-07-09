from discord.ext import commands
import discord
from gmail_reminder_server import *
import os, json
from dotenv import load_dotenv
import datetime, time
from fastapi import FastAPI, Request, BackgroundTasks
import psycopg2, threading, requests

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

@app.post('/discord')
async def discord_run(request: Request):
    request_data = await request.json()
    try:
        response = requests.post(url='PLACEHOLDER', json=request_data)
        print(response.status_code)
        print(response.json())
    except Exception as e:
        print(e)

# Need to rewrite the server to only add reminders and times to a database and then it'll tick forward and send reminders as needed.

@app.post('/reminder')
async def insert_reminder(request: Request):
    request_data = await request.json()
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
    except Exception as e:
        print(e)
    query = """
        INSERT INTO Reminders(reminder_name, email, frequency, date_made, target_time, fuzziness)
        VALUES
                (
                    %s, %s, %s, (current_date), %s, %s
                );
    """
    values = [request_data['reminder_name'], request_data['email'], request_data['frequency'], request_data['target_time'], request_data['fuzziness']]
    cur.execute(query, values)
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
    
# bot.run(os.getenv('DISCORD_TOKEN'))
