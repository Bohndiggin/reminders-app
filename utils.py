import discord, schedule, asyncio, time, requests, os, json
from discord.ext import commands
from dotenv import load_dotenv
from datetime import date, time, datetime, timedelta
from faker import Faker


load_dotenv()
server_url = os.getenv('SERVER_URL')

fake = Faker()

class Avenue: # Avenues are ways to remind the user.
    def __init__(self, url, reminder_name: str, message: str, endpoint) -> None:
        self.url = url
        self.reminder_name = reminder_name
        self.message = message
        self.endpoint = endpoint
    
    def remind(self):
        url_to_request = self.url + self.endpoint
        request_body = {
            'subject': self.reminder_name,
            'message': self.message
        }
        request_json = json.dumps(request_body)
        reminder_request = requests.post(url_to_request, request_json)
        print(reminder_request.json())

# FREQUENCY NEEDS TO BE A LIST OF DAYS OF THE WEEK
class Reminder:
    def __init__(self, reminder_name: str, target_time: datetime, fuzziness, avenues=[], frequency='Once') -> None:
        self.reminder_name = reminder_name
        self.target_time = target_time
        self.fuzziness = timedelta(minutes=fuzziness)
        self.avenues = avenues
        self.frequency = frequency
        self.complete_status = False
        self.set_offset()
    
    def remind(self):
        while datetime.now() < self.real_offset:
            time.sleep(60)
        for i in self.avenues:
            i.remind()

    def complete(self):
        self.complete_status = True
    
    def reset_complete(self):
        self.complete_status = False

    # def date_rollover(self):
    #     self.reset_complete()

    def set_recurrance(self):
        pass

    def set_offset(self):
        fore_fuzzy = self.target_time - self.fuzziness
        aft_fuzzy = self.target_time + self.fuzziness
        self.real_offset = fake.date_time_between(start_date=fore_fuzzy, end_date=aft_fuzzy)

    def __repr__(self) -> str:
        return f'{self.reminder_name}, a task you need to do {self.frequency}'
    
    def add_avenue(self, url, endpoint):
        self.avenues.append(Avenue(url, self.reminder_name, str(self), endpoint))
    

if __name__ == '__main__':
    # discord_test = Avenue(server_url, 'reminder name', 'message', '/discord')
    # discord_test.remind()
    print(datetime.now())
    reminder_test = Reminder('Do the Dishes', datetime.now() + timedelta(minutes=5), 1)
    print(reminder_test.real_offset)
    reminder_test.add_avenue(server_url, '/gmail')
    reminder_test.add_avenue(server_url, '/discord')
    reminder_test.remind()
    print(reminder_test.real_offset)
    print(datetime.now())