import discord, schedule, asyncio, time, requests, os, json
from discord.ext import commands
from dotenv import load_dotenv
import datetime
from faker import Faker


load_dotenv()
server_url = os.getenv('SERVER_URL')

fake = Faker()

class Avenue: # Avenues are ways to remind the user.
    def __init__(self, url, parent_reminder_name: str, message, endpoint, email='') -> None:
        self.url = url
        self.parent_reminder_name = parent_reminder_name
        self.message = message
        self.endpoint = endpoint
        self.email = email
    
    def remind(self):
        url_to_request = self.url + self.endpoint
        request_body = {
            'subject': self.parent_reminder_name,
            'message': self.message,
            'email': self.email
        }
        request_json = json.dumps(request_body)
        reminder_request = requests.post(url_to_request, request_json)
        print(reminder_request.json())

    def __repr__(self) -> str:
        return f'{self.parent_reminder_name} avenue with message {self.message}'

# FREQUENCY NEEDS TO BE A LIST OF DAYS OF THE WEEK
class Reminder:
    def __init__(self, id, reminder_name: str, target_time:datetime.time, fuzziness=1, frequency='Once', email='', date_made=datetime.time, avenues_sql='') -> None:
        self.id = id
        self.reminder_name = reminder_name
        today = datetime.date.today()
        self.target_time = datetime.datetime.combine(today, target_time)
        self.fuzziness = datetime.timedelta(minutes=fuzziness)
        self.avenues = []
        self.frequency = frequency
        self.complete_status = False
        self.email = email
        self.date_made = date_made
        self.avenues_sql = avenues_sql
        self.set_offset()
        # print(self.real_offset)
    
    def remind(self): # 
        now = datetime.datetime.now()
        now_no_s_ms = now.replace(second=0, microsecond=0)
        if now_no_s_ms == self.real_offset:
            # print('same')
            for i in self.avenues:
                i.remind()
            return True
        else:
            return False

    def complete(self):
        self.complete_status = True
    
    def reset_complete(self):
        self.complete_status = False

    def set_recurrance(self):
        pass

    def set_offset(self):
        fore_fuzzy = self.target_time - self.fuzziness
        aft_fuzzy = self.target_time + self.fuzziness
        self.real_offset = fake.date_time_between(start_date=fore_fuzzy, end_date=aft_fuzzy)
        self.real_offset = self.real_offset.replace(second=0, microsecond=0)

    def __repr__(self) -> str:
        return f'{self.reminder_name}, a task you need to do {self.frequency}.'
    
    def add_avenue(self=None, url='Server', endpoint='/endpoint'):
        new_avenue = Avenue(url, self.reminder_name, str(self), endpoint, self.email)
        self.avenues.append(new_avenue)
    

# if __name__ == '__main__':
    # discord_test = Avenue(server_url, 'reminder name', 'message', '/discord')
    # discord_test.remind()
    # print(datetime.datetime.now())
    # reminder_test = Reminder('Do the Dishes', datetime.datetime.now() + datetime.timedelta(minutes=5), 1)
    # print(reminder_test.real_offset)
    # reminder_test.add_avenue(server_url, '/gmail')
    # reminder_test.add_avenue(server_url, '/discord')
    # reminder_test.remind()
    # print(reminder_test.real_offset)
    # print(datetime.now())