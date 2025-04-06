# nullbot_db_helper.py
import os

from dotenv import load_dotenv

from datetime import datetime

load_dotenv()

# Importing module 
import mysql.connector

# Creating connection object
mydb = mysql.connector.connect(
    host = os.getenv('DB_HOST'),
    user = os.getenv('DB_USER'),
    password = os.getenv('DB_PASSWORD')
)

# Cursor to execute statements
cursor = mydb.cursor()
cursor.execute("USE nullbot")

class User:
    def __init__(self, user_id, user_name, discord_id):
        self.user_id = user_id
        self.user_name = user_name
        self.discord_id = discord_id

# returns the user in the users table by DBID.
def get_user(user_id):
    user = None

    try:
        cursor.execute("SELECT * FROM users "
                       "WHERE user_id = " + str(user_id) + ";")
        result = cursor.fetchone()
        if(result is not None):
            user = User(result[0], result[1], result[2])
    except Exception as e:
        print(e)
    
    return user

# returns the user in the users table by Discord ID.
def get_user_by_discord_id(discord_id):
    user = None

    try:
        cursor.execute("SELECT * FROM users "
                       "WHERE discord_id = " + str(discord_id) + ";")
        result = cursor.fetchone()
        if(result is not None):
            user = User(result[0], result[1], result[2])
    except Exception as e:
        print(e)
    
    return user

# returns the DBID from get_user. if the user does not exist, then create a row in the users table first.
def create_user(user_name, discord_id):
    user_id = None

    try:
        user = get_user_by_discord_id(discord_id)
        if(user is None):
            cursor.execute("INSERT INTO users (user_name, discord_id) "
                        "VALUES ('" + str(user_name) + "', " + str(discord_id) +");")
            user_id = cursor.lastrowid
            cursor.execute("COMMIT;")
        else:
            user_id = user.user_id
    except Exception as e:
        print(e)
    
    return user_id

class Context:
    def __init__(self, context_id, user, guild_id, channel_id):
        self.context_id = context_id
        self.user = user
        self.guild_id = guild_id
        self.channel_id = channel_id

# return context with the context id
def get_context(context_id):
    context = None

    try:
        cursor.execute("SELECT * FROM context "
                       "WHERE context_id = " + str(context_id) + ";")
        result = cursor.fetchone()
        if(result is not None):
            context_id = result[0]
            user = get_user(result[1])
            guild_id = result[2]
            channel_id = result[3]
            context = Context(context_id, user, guild_id, channel_id)
    except Exception as e:
        print(e)
    
    return context

# creates a row in the context table and returns the DBID.
def create_context(user_id, guild_id, channel_id):
    context_id = None

    try:
        cursor.execute("INSERT INTO context (user_id, guild_id, channel_id) "
                       "VALUES (" + str(user_id) + ", " + str(guild_id) + ", " + str(channel_id) +");")
        context_id = cursor.lastrowid
        cursor.execute("COMMIT;")
    except Exception as e:
        print(e)
    
    return context_id

# delete a row from the context table
def delete_context(context_id):
    try:
        if(context_id is not None):
            cursor.execute("DELETE FROM context "
                        "WHERE context_id = " + str(context_id) + ";")
            context_id = cursor.lastrowid
            cursor.execute("COMMIT;")
    except Exception as e:
        print(e)

class Reminder:
    def __init__(self, reminder_id, reminder_text, reminder_date, context):
        self.reminder_id = reminder_id
        self.reminder_text = reminder_text
        self.reminder_date = reminder_date
        self.context = context

# returns a list of all reminders
def get_all_reminders():
    reminder_list = []

    try:
        cursor.execute("SELECT * FROM reminders;")
        result_list = cursor.fetchall()
        if(result_list is not None):
            for result in result_list:
                reminder_id = result[0]
                reminder_text = result[1]
                reminder_date = result[2]
                context = get_context(result[3])
                reminder_list.append(Reminder(reminder_id, reminder_text, reminder_date, context))
    except Exception as e:
        print(e)
    
    return reminder_list

# creates a row in the reminders
def create_reminder(reminder_text, reminder_date, context_id):
    reminder_id = None

    try:
        cursor.execute("INSERT INTO reminders (reminder_text, reminder_date, context_id) "
                       "VALUES ('" + str(reminder_text) + "', '" + str(reminder_date) + "', " + str(context_id) +");")
        reminder_id = cursor.lastrowid
        cursor.execute("COMMIT;")
    except Exception as e:
        print(e)
    
    return reminder_id

# delete a row from the reminders table
def delete_reminder(reminder_id):
    try:
        if(reminder_id is not None):
            cursor.execute("DELETE FROM reminders "
                        "WHERE reminder_id = " + str(reminder_id) + ";")
            context_id = cursor.lastrowid
            cursor.execute("COMMIT;")
    except Exception as e:
        print(e)