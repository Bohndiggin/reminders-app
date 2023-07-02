# THIS FILE IS TO TRACK TIME AND REGULARLY CHECK DB
import datetime, time, os, requests, schedule # LOOK UP SCHEDULE DOCUMENATION FOR "TODAY"
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DB_API")

try:
    conn = psycopg2.connect(db_url)
    print('Yay')
except Exception as e:
    print(e)

# Every hour, gather the next 90 minutes worth of reminders and sort them
# AT midnight, change the day of the week
# "EVERY OTHER TUESDAY, WEDNESDAY at 10pm"

def remind_query():
    print('A reminder')

schedule.every().hour.do(remind_query) # DAILY MEANS YOU MIGHT NOT NEED A DAY SPECIFIED

def main():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()

