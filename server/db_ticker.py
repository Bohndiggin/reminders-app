# THIS FILE IS TO TRACK TIME AND REGULARLY CHECK DB
# Every hour, gather the next 90 minutes worth of reminders and sort them
import schedule
from dotenv import load_dotenv
from utils import *
import psycopg2, psycopg2.extras
from multiprocessing import Process
from pydantic import BaseModel

load_dotenv()

db_url = os.getenv("DB_API")
server_url = os.getenv('SERVER_URL')


next_90 = []
successfully_reminded = []

def reminder_func_paralell(obj, successfully_reminded): # This allows the main remind_it() to spawn more reminders than can be processed in a minute, that way we don't run out of time to remind.
    reminder_worked = obj.remind() # if the reminder suceeded, it returns true
    if reminder_worked == True:
        successfully_reminded.append(obj.id)
        print(f'reminded! ID: {obj.id} __ Offset: {obj.real_offset}')
    elif reminder_worked == False:
        pass
    return 'complete'

def remind_query(): # This will query the database and create objects for each reminder. Should fire every 60 min. It then gathers the next 90 min (on a -2 min offset) of reminders.
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
                SELECT * FROM "public"."reminders" AS reminders
                JOIN Users ON reminders.user_id = Users.user_id
                WHERE reminders.frequency LIKE '%{now.weekday()}%'
                AND target_time_local_to_server BETWEEN '{str_now}' and '{str_now_90}'
                """)
    answer = cur.fetchall()
    try:
        id_list = [x.id for x in next_90]
    except:
        id_list = []
    for row in answer:
        temp_reminder = None      
        temp_reminder = Reminder(**dict(row))
        temp_avenue_list = temp_reminder.avenues_sql.split(' ')
        for avenue in temp_avenue_list:
            temp_reminder.add_avenue(server_url, avenue) # Need to add avenues to DB so I know which ones to add
        if temp_reminder.id in id_list:
            continue
        elif temp_reminder.id not in successfully_reminded:
            next_90.append(temp_reminder)
    cur.close()
    conn.close()
    if len(next_90) == 0:
        print('remind_query returned no reminders')
    return next_90

def remind_it(): # makes a list of reminder processes and starts them all.
    global next_90, successfully_reminded
    try:
        for i in next_90:
            # print(i)
            if i.id in successfully_reminded:
                print('skipped: already reminded')
                continue
            else:
                process_list = []
                process_list.append(Process(target=reminder_func_paralell, kwargs={"obj": i, "successfully_reminded": successfully_reminded}))
                for j in process_list:
                    j.start()
        next_90 = [x for x in next_90 if x.id not in successfully_reminded]
        print('______________', datetime.datetime.now())
    except Exception as e:
        print(e)

def remind_query_try():
    try:
        remind_query()
    except Exception as e:
        print(e)

def remind_it_try():
    try:
        remind_it()
    except Exception as e:
        print(e)

schedule.every().hour.do(remind_query_try)
schedule.every().minute.do(remind_it_try)

def main(): 
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    remind_query_try()
    remind_it_try()
    main()