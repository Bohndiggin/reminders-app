from discord.ext import commands
import asyncio
import discord, os, datetime
from gmail_reminder_server import *
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import psycopg2, pytz
import subprocess as sp
from pydantic import BaseModel
from google_calendar import calendar_add

load_dotenv()

app = FastAPI()
intents = discord.Intents.all()
db_url = os.getenv("DB_API")
bot = commands.Bot(command_prefix='!', intents=intents)
ticker = sp.Popen(['python', 'db_ticker.py'])
# bot.run(os.getenv('TOKEN'))

class ReminderItem(BaseModel):
    reminder_name: str
    email: str
    frequency: str
    target_time: str
    target_time_timezone: str
    fuzziness: int
    avenues_sql: str

class GmailItem(BaseModel):
    subject: str
    message: str
    email: str
    discord_id: int | None # Discord ID. Might need to get from oauth

class CalendarItem(BaseModel):
    subject: str
    message: str
    email: str | None
    discord_id: int | None # Discord ID. Might need to get from oauth

class DiscordItem(BaseModel):
    subject: str
    message: str
    email: str | None
    discord_id: int # Discord ID. Might need to get from oauth

class RemindDeleteItem(BaseModel):
    id: int

def restart_ticker():
    global ticker
    sp.Popen.terminate(ticker)
    ticker = sp.Popen(['python', 'db_ticker.py'])
   
@app.on_event('startup')
async def startup_event():
    asyncio.create_task(bot.start(os.getenv('DISCORD_TOKEN')))
    await asyncio.sleep(4)
    print(f'{bot.user} has connected to discord!')

@app.get('/')
async def root():
    return {"message": "Hello World"}

@app.post('/calendar')
async def calendar_run(calendar_request: CalendarItem):
    calendar_add(calendar_request.message, calendar_request.message)
    return {"message": "success"}

@app.post('/gmail')
async def gmail_run(gmail_request: GmailItem):
    gmail_bot_main(gmail_request.subject, gmail_request.message, gmail_request.email)
    return {"message": "success"}

@app.post("/discord")
async def start_bot(discord_item: DiscordItem):
    user = await bot.fetch_user(discord_item.discord_id)
    await user.send(discord_item.message)
    print('sent to ' , discord_item.discord_id)
    # await bot.close()
    return {"status": "success"}

# Need to rewrite the server to only add reminders and times to a database and then it'll tick forward and send reminders as needed.

@app.post('/reminder')
async def insert_reminder(reminder_request: ReminderItem):
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
    except Exception as e:
        print(e)
    # Next section is to sort out timezones. The server is in US/Mountain time. All reminders are changed to US/Mountain, but the original Timezone is stored just in case.
    time_zone = pytz.timezone(reminder_request.target_time_timezone)
    target_time_zone = pytz.timezone('US/Mountain')
    target_time = datetime.datetime.strptime(reminder_request.target_time, '%H:%M:%S')
    target_time_non_local = time_zone.localize(target_time)
    localized_time = target_time_non_local.astimezone(target_time_zone)
    localized_time_str = localized_time.strftime('%H:%M:%S')
    query = """
        INSERT INTO Reminders(reminder_name, email, frequency, date_made, target_time_local_to_server, target_time_timezone, fuzziness, avenues_sql)
        VALUES
                (
                    %s, %s, %s, (current_date), %s, %s, %s, %s
                );
    """
    values = [
        reminder_request.reminder_name,
        reminder_request.email,
        reminder_request.frequency,
        localized_time_str,
        reminder_request.target_time_timezone,
        reminder_request.fuzziness,
        reminder_request.avenues_sql
    ]
    cur.execute(query, values)
    conn.commit()
    cur.close()
    conn.close()
    restart_ticker()
    return {"message": "reminder post sucsessful"}

@app.delete('/reminder')
async def delete_reminder(reminder_request: RemindDeleteItem):
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
    except Exception as e:
        print(e)
    try:
        cur.execute("""
            DELETE FROM Reminders WHERE id = {id};
        """.format(id=reminder_request.id))
        conn.commit()
        cur.close()
        conn.close()
        restart_ticker()
        return {"message": "Deletion Sucessful of {id}".format(id=reminder_request.id)}
    except Exception as e:
        print('Deletion Error', e)
        cur.close()
        conn.close()
        restart_ticker()
        return {"message": "Deletion NOT Sucessful of {id}, for reason ".format(id=reminder_request.id), "error": e}
