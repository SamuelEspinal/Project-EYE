# nullbot_db_setup.py
import os
from dotenv import load_dotenv

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
cursor.execute("CREATE DATABASE IF NOT EXISTS nullbot;")
cursor.execute("USE nullbot;")

# Drop tables
cursor.execute("DROP TABLE reminders;")
cursor.execute("DROP TABLE context;")
cursor.execute("DROP TABLE users;")

# Create tables
cursor.execute("CREATE TABLE users ("
               "user_id int PRIMARY KEY AUTO_INCREMENT,"
               "user_name varchar(255) NOT NULL, "
               "discord_id bigint UNIQUE NOT NULL"
               ");")
cursor.execute("CREATE UNIQUE INDEX i_user_id ON users (user_id);")

cursor.execute("CREATE TABLE context ("
               "context_id int PRIMARY KEY AUTO_INCREMENT,"
               "user_id int NOT NULL,"
               "guild_id bigint NOT NULL,"
               "channel_id bigint NOT NULL,"
               "FOREIGN KEY (user_id) REFERENCES users (user_id)"
               ");")
cursor.execute("CREATE UNIQUE INDEX i_context_id ON context (context_id);")

cursor.execute("CREATE TABLE reminders ("
               "reminder_id int PRIMARY KEY AUTO_INCREMENT,"
               "reminder_text varchar(255) NOT NULL,"
               "reminder_date datetime NOT NULL,"
               "context_id int NOT NULL,"
               "FOREIGN KEY (context_id) REFERENCES context (context_id)"
               ");")
cursor.execute("CREATE UNIQUE INDEX i_reminder_id ON reminders (reminder_id);")