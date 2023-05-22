import random

class Reminder:
    def __init__(self, text, target_time, fuzziness, frequency='once') -> None:
        self.text = text
        self.target_time = target_time
        self.fuzziness = fuzziness
        self.frequency = frequency
        self.complete_status = False
    
    def remind(self):
        pass

    def complete(self):
        self.complete_status = True
    
    def reset_complete(self):
        self.complete_status = False

    def __repr__(self) -> str:
        return f'{self.text}, a task you need to do {self.frequency}'
    

