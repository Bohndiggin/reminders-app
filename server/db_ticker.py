# THIS FILE IS TO TRACK TIME AND REGULARLY CHECK DB
import requests, schedule, sys # LOOK UP SCHEDULE DOCUMENATION FOR "TODAY"
from dotenv import load_dotenv
from utils import *
import psycopg2, psycopg2.extras

load_dotenv()

db_url = os.getenv("DB_API")
server_url = os.getenv('SERVER_URL')


next_90 = []
successfully_reminded = []

# Every hour, gather the next 90 minutes worth of reminders and sort them
# AT midnight, change the day of the week
# "EVERY OTHER TUESDAY, WEDNESDAY at 10pm"
# ADD time as a parameter so I can run queries immediately

def remind_query():
    global next_90, successfully_reminded
    try:
        conn = psycopg2.connect(db_url)
        print('Connected to Database...')
    except Exception as e:
        print('Database Connection FAIL:', e)
    now = datetime.datetime.now() - datetime.timedelta(minutes=2)
    str_now = now.strftime('%H:%M:%S')
    print(str_now)
    now_90 = now + datetime.timedelta(minutes=90)
    str_now_90 = now_90.strftime('%H:%M:%S')
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"""
                SELECT * FROM "public"."reminders" reminders
                WHERE reminders.frequency LIKE '%{now.weekday()}%'
                AND target_time BETWEEN '{str_now}' and '{str_now_90}'
                """)
    answer = cur.fetchall()
    try:
        id_list = [x.id for x in next_90]
    except:
        id_list = []
    for row in answer:
        temp_reminder = None      
        temp_reminder = Reminder(**dict(row))
        temp_reminder.add_avenue(server_url, '/gmail') # Need to add avenues to DB so I know which ones to add
        if temp_reminder.id in id_list:
            continue
        elif temp_reminder.id not in successfully_reminded:
            next_90.append(temp_reminder)
    cur.close()
    conn.close()
    if len(next_90) == 0:
        print('remind_query returned no reminders')
    return next_90

def remind_it():
    global next_90, successfully_reminded
    try:
        to_be_popped = []
        for i in next_90:
            # print(i)
            if i.id in successfully_reminded:
                print('skipped: already reminded')
                continue
            else:
                reminder_worked = i.remind()
                if reminder_worked == True:
                    successfully_reminded.append(i.id)
                    to_be_popped.append(i.id)
                    print('reminded!')
                elif reminder_worked == False:
                    print('skipped: incorrect time')
                    continue
        next_90 = [x for x in next_90 if x.id not in successfully_reminded]
        print('______________')
    except Exception as e:
        print(e)

schedule.every().hour.do(remind_query)

def main(): # MAKE IT SET TO BUSY WHEN IT'S BUSY _ Make 2 QUEUES IN-flight and staged
    while True:
        schedule.run_pending()
        time.sleep(60)
        remind_it()

def test():
    test_time = datetime.datetime(2023, 7, 5, 5, 29, 0)
    remind_query(now=test_time)
    pass

if __name__ == '__main__':
    # seed_funciton()
    # add_function()
    remind_query()
    remind_it()
    # test()
    main()