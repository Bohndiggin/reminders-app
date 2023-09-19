import asyncio
import os, datetime
from gmail_reminder_server import *
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import psycopg2, pytz
import subprocess as sp
from pydantic import BaseModel
from google_calendar import calendar_add
from discord_reminder_server import bot, send_reminder_discord
import logging
from logging.handlers import RotatingFileHandler
from starlette.responses import FileResponse 

load_dotenv()

app = FastAPI()
# intents = discord.Intents.all()
db_url = os.getenv("DB_API")
app.mount('/', StaticFiles(directory="../client", html=True), name='html')
ticker = sp.Popen(['python', 'db_ticker.py'])
REMINDERSEND = 25 # TODO change to only write remindersend info
logging.addLevelName(REMINDERSEND, 'REMINDERSEND')

def reminder_send_log(self, message, *args, **kws):
    if self.isEnabledFor(REMINDERSEND):
        self._log(REMINDERSEND, message, args, **kws)

logging.Logger.reminder_send_log = reminder_send_log

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
log_file = './log'
my_handler = RotatingFileHandler(log_file, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)


app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

# bot.run(os.getenv('TOKEN'))

class ReminderItem(BaseModel):
    reminder_name: str
    email: str
    frequency: str
    target_time: str
    target_time_timezone: str
    fuzziness: int
    avenues_sql: str

class DelayRequestItem(BaseModel):
    reminder_name: str
    email: str
    delay_length: int

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
    app_log.info('Startup Complete, Bot Ready')

@app.get('/')
async def read_index():
    return FileResponse('../client/index.html')

@app.post('/calendar')
async def calendar_run(calendar_request: CalendarItem):
    # calendar_add(calendar_request.message, calendar_request.message)
    return {"message": "NOT READY"}

@app.post('/gmail')
async def gmail_run(gmail_request: GmailItem):
    gmail_bot_main(gmail_request.subject, gmail_request.message, gmail_request.email)
    app_log.reminder_send_log(f'Email Message: {gmail_request.message} Sent to user: {gmail_request.email}')
    return {"message": "success"}

@app.post("/discord")
async def start_bot(discord_item: DiscordItem):
    await send_reminder_discord(discord_item=discord_item)
    app_log.reminder_send_log(f'Discord Message: {discord_item.message} Sent to user: {discord_item.discord_id}')
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
        SELECT * FROM Users
        WHERE Users.email = %s
    """
    values = [
        reminder_request.email
    ]
    cur.execute(query, values)
    answer = cur.fetchone()
    
    conn.commit()
    query = """
        INSERT INTO Reminders(reminder_name, user_id, frequency, date_made, target_time_local_to_server, target_time_timezone, fuzziness, avenues_sql)
        VALUES
                (
                    %s, %s, %s, (current_date), %s, %s, %s, %s
                );
    """
    values = [
        reminder_request.reminder_name,
        answer[0],
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

@app.post('/delay')
async def delay_task(delay_request: DelayRequestItem): 
    # HOW DO? Maybe the object can handle the update to the avenue? What happens to the reminded??
    # try:
    #     conn = psycopg2.connect(db_url)
    #     cur = conn.cursor()
    # except Exception as e:
    #     print(e)
    # query = """
    #     UPDATE Reminders
    #     SET target_time_local_to_server = %s
    #     FROM Users AS u
    #     WHERE Reminders.user_id = u.user_id
    #     AND u.email = %s
    #     AND Reminders.reminder_name = %s
    # """
    # cur.execute(query, values)
    # conn.commit()
    # cur.close()
    # conn.close()
    # restart_ticker()
    # return {"message": "Deletion Sucessful of {id}".format(id=reminder_request.id)}
    pass