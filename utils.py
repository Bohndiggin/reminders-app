import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
from datetime import date, time, datetime, timedelta
from faker import Faker
import asyncio
import time
# from discord_bot import *
import requests
import json


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


class Reminder:
    def __init__(self, reminder_name: str, target_time: datetime, fuzziness, avenues=[], frequency='Once') -> None:
        self.reminder_name = reminder_name
        self.target_time = target_time
        self.fuzziness = timedelta(minutes=fuzziness)
        self.avenues = avenues
        self.frequency = frequency
        self.complete_status = False
    
    def remind(self):
        pass

    def complete(self):
        self.complete_status = True
    
    def reset_complete(self):
        self.complete_status = False

    def date_rollover(self):
        self.reset_complete()

    def set_offset(self):
        fore_fuzzy = self.target_time - self.fuzziness
        aft_fuzzy = self.target_time + self.fuzziness
        self.real_offset = fake.date_time_between(start_date=fore_fuzzy, end_date=aft_fuzzy)

    def __repr__(self) -> str:
        return f'{self.reminder_name}, a task you need to do {self.frequency}'
    

if __name__ == '__main__':
    discord_test = Avenue(server_url, 'reminder name', 'message', '/discord')
    discord_test.remind()