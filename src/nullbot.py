# nullbot.py
import os
import time
import threading
import asyncio
import discord
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime
# import bigram
# import bigramModel2

#Import tool functions
from helpers.nullbot_helper import *
from db.nullbot_db_helper import *

#Import command helper functions
import helpers.reminder.reminder_helper as reminder_helper
import helpers.weather.weather_helper as weather_helper

#Bot initialization
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='null ', intents=intents)

#### BOT EVENTS ####
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

#### REMINDER COMMANDS ####
@bot.command()
async def remind(ctx, *args):
    await reminder_helper.remind(ctx, *args)

@bot.command()
async def showreminders(ctx):
    await reminder_helper.showReminders(ctx)

@bot.command()
async def checkreminders(ctx):
    await reminder_helper.checkReminders(ctx, bot)

#### WEATHER COMMANDS ####
@bot.command()
async def weather(ctx, *, location="Orlando"): #default location is Orlando
    print(f"Received location: {location}")
    await weather_helper.weather(ctx, location)

#### DEBUG COMMANDS ####
@bot.command()
async def saysomething(ctx):
    await bot.get_guild(ctx.guild.id).get_channel(ctx.channel.id).send("successful")

@bot.command()
async def say(ctx, *args):
    if len(args) != 0:
        reply = ' '.join(args)
        await ctx.send(reply)


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