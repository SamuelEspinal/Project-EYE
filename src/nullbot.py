# nullbot.py
import os
import time
import threading
import asyncio

# import bigram
# import bigramModel2

from datetime import datetime

from nullbot_helper import *
from nullbot_db_helper import *

import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='null ', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    if(message.author == bot.user):
        return

    if(check_greeting(message)):
        response = create_greeting(message)
        await message.channel.send(response)

    await bot.process_commands(message)

@bot.command()
async def say(ctx, *args):
    if len(args) != 0:
        reply = ' '.join(args)
        await ctx.send(reply)

@bot.command()
async def remind(ctx, *args):
    usage = ("*null remind [time] [date (optional)] [reminder]*\n\n"
             "Usage: NullBot will ping you at the specified time (24h format, EST) and date with the reminder message.\n\n"
             "Accepted date formats: *YYYY-MM-dd* or *MM-dd-yyyy* (may substitute dashes with slashes)\n"
             "Accepted time formats: *HH:mm* or *HH:mm:ss*")
    if(len(args) >= 2):
        time_string = args[0]
        date_string = args[1]
        time = validate_time(time_string)
        date = validate_date(date_string)
        bot_response = None
        reminder_text = None
        if(time is not None):
            if(date is not None):
                if len(args) > 2:
                    reminder_text = ' '.join(args[2:])
                    bot_response = "I'll remind you to \"" + reminder_text + "\" at " + time_string + " on " + date_string
                else:
                    await ctx.send("No reminder message provided")
            else:
                reminder_text = ' '.join(args[1:])
                bot_response = "I'll remind you to \"" + reminder_text + "\" at " + time_string
        else:
            await ctx.send("Time must to be in the correct format (Type *null remind* for help)")
        if(reminder_text is not None):
            user_id = create_user(ctx.author.name, ctx.author.id)
            if(user_id is not None):
                context_id = create_context(user_id, ctx.guild.id, ctx.channel.id)
                if(context_id is not None):
                    if(date is None):
                        date = datetime.strftime(datetime.now(), "%Y-%m-%d")
                    datetime_string = date + " " + time
                    reminder_id = create_reminder(reminder_text, datetime_string, context_id)
                    if(reminder_id is not None):
                        await ctx.send(bot_response)
                else:
                    await ctx.send("Failed to create context row for user_id = " + str(user_id))
            else:
                await ctx.send("Failed to create users row for Discord ID " + str(ctx.author.id))
    else:
        await ctx.send(usage)

@bot.command()
async def saysomething(ctx):
    await bot.get_guild(ctx.guild.id).get_channel(ctx.channel.id).send("successful")

@bot.command()
async def showreminders(ctx):
    reminder_list = get_all_reminders()
    index = 1
    bot_response = ""
    for reminder in reminder_list:
        bot_response += str(index) + ". Remind " + reminder.context.user.user_name + " to \"" + reminder.reminder_text + "\" on " + str(reminder.reminder_date) + "\n"
        index += 1
    await ctx.send(bot_response)

@bot.command()
async def checkreminders(ctx):
    reminder_list = get_all_reminders()
    now = datetime.now()

    if(reminder_list is not None and len(reminder_list) > 0):
        for reminder in reminder_list:
            guild = bot.get_guild(reminder.context.guild_id)
            channel = guild.get_channel(reminder.context.channel_id)
            if(reminder.reminder_date < now):
                await channel.send("<@" + str(reminder.context.user.discord_id) + ">, reminder to \"" + reminder.reminder_text) + "\""
                delete_reminder(reminder.reminder_id)
                delete_context(reminder.context.context_id)
            else:
                await channel.send("I will remind " + str(reminder.context.user.user_name) + " to \"" + reminder.reminder_text + "\" on " + str(reminder.reminder_date))
    else:
        await ctx.send("There are no pending reminders")


# @bot.command()
# async def createme(ctx):
#     user_id = await create_user(ctx.author.name, ctx.author.id)
#     if(user_id is not None):
#         await ctx.send("Registered " + ctx.author.name + " (Discord ID = " + str(ctx.author.id) + ", DBID = " + str(user_id) + ")!")
#     else:
#         await ctx.send("Failed to register " + ctx.author.name + " (Discord ID = " + str(ctx.author.id) + ", DBID = " + str(user_id) + ")!")

# @bot.command()
# async def viewme(ctx):
#     user_id = await get_user(ctx.author.id)
#     if(user_id is not None):
#         await ctx.send("User with Discord ID " + str(ctx.author.id) + " found with DBID " + str(user_id))

# @bot.command()
# async def generate1(ctx):
#     response = bigram.torchGenerate()
#     if response:
#         await ctx.send(response)

# @bot.command()
# async def generate2(ctx):
#     response = bigramModel2.torchGenerate()
#     if response:
#         await ctx.send(response)

bot.run(TOKEN)

# def reminder_timer():
#     while True:
#         time.sleep(5)
#         try:
#             asyncio.run(check_reminders())
#         except Exception as e:
#             print(e)