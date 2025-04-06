# nullbot_helper.py
from datetime import datetime
from nullbot_db_helper import *

greeting_list = ["hi", "hey", "hello", "whats up", "what's up", "sup", "yo", "hows it going", "how's it going", "greetings"]

date_format_list = ["%Y-%m-%d", "%m-%d-%Y", "%Y/%m/%d", "%m/%d/%Y"]
time_format_list = ["%H:%M:%S", "%H:%M"]

def check_greeting(message):
    message_string = message.content.lower()

    if("nullbot" in message_string):
        for greeting in greeting_list:
            if(message_string.startswith(greeting + " nullbot")):
                return True
    
    return False

def create_greeting(message):
    greeting = f"Hey {message.author.name}"
    current_hour = datetime.now().hour

    if(current_hour >= 5 and current_hour < 12):
        greeting = f"Good morning {message.author.name}"
    elif(current_hour >= 12 and current_hour < 16):
        greeting = f"Good afternoon {message.author.name}"
    elif(current_hour >= 16 and current_hour < 20):
        greeting = f"Good evening {message.author.name}"
    
    print(message.author.id)

    return greeting

def validate_date(date_string):
    date = None

    for date_format in date_format_list:
        try:
            date = datetime.strptime(date_string, date_format)
        except ValueError:
            pass
    if(date is not None):
        date = datetime.strftime(date, "%Y-%m-%d")
    
    return date
    
def validate_time(time_string):
    time = None
    
    for time_format in time_format_list:
        try:
            time = datetime.strptime(time_string, time_format)
        except ValueError:
            pass
    if(time is not None):
        time = datetime.strftime(time, "%H:%M:%S")
    
    return time