import random
from datetime import date, time, datetime, timedelta
from faker import Faker
fake = Faker()

class Avenue: # Avenues are ways to remind the user.
    def __init__(self, url) -> None:
        self.url = url

class GmailAvenue(Avenue):
    def __init__(self, url) -> None:
        super().__init__(url)

    def remind(self, text):
        pass

class DiscordAvenue(Avenue):
    def __init__(self, url) -> None:
        super().__init__(url)

    def remind(self, text):
        pass

class CalendarAvenue(Avenue):
    def __init__(self, url) -> None:
        super().__init__(url)
    
    def remind(self, text):
        pass

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