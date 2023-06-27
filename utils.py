import random
import time
from faker import Faker
fake = Faker()

class Avenue: # Avenues are ways to remind the user.
    def __init__(self) -> None:
        pass
    

class Reminder:
    def __init__(self, text, target_time, fuzziness, avenues=[], frequency='once') -> None:
        self.text = text
        self.target_time = target_time
        self.fuzziness = fuzziness
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
        return f'{self.text}, a task you need to do {self.frequency}'
    


