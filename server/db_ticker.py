# THIS FILE IS TO TRACK TIME AND REGULARLY CHECK DB
import datetime, time, os, requests, schedule, sys # LOOK UP SCHEDULE DOCUMENATION FOR "TODAY"
import psycopg2, psycopg2.extras
from dotenv import load_dotenv
from utils import *

load_dotenv()

db_url = os.getenv("DB_API")


next_90 = []

# Every hour, gather the next 90 minutes worth of reminders and sort them
# AT midnight, change the day of the week
# "EVERY OTHER TUESDAY, WEDNESDAY at 10pm"

def remind_query():
    global next_90
    try:
        conn = psycopg2.connect(db_url)
        print('Connected to Database...')
    except Exception as e:
        print('Database Connection FAIL:', e)
    next_90 = []
    now = datetime.datetime.now()
    now_90 = now + datetime.timedelta(minutes=90)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"""
                SELECT * FROM "public"."reminders" reminders
                WHERE reminders.frequency LIKE '%{now.weekday()}%'
                """)
    answer = cur.fetchall()
    answer_list = []
    for row in answer:
        answer_list.append(dict(row))
    print(answer_list[0])
    cur.close()
    conn.close()

schedule.every().hour.do(remind_query) # DAILY MEANS YOU MIGHT NOT NEED A DAY SPECIFIED

def main():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    remind_query()
    # main()

