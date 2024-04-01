# bot.py
import os

import bigram
import bigramModel2

from datetime import datetime

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
    if message.author == bot.user:
        return

    if message.content.lower() == 'hi nullbot' or message.content.lower() == 'hey nullbot' or message.content.lower() == 'hello nullbot':
        response = 'Hey'
        await message.channel.send(response)

    await bot.process_commands(message)

@bot.command()
async def say(ctx, *args):
    if len(args) != 0:
        reply = ' '.join(args)
        await ctx.send(reply)

@bot.command()
async def remind(ctx, *args):
    if len(args) > 1:
        reminder = ' '.join(args[1:])
        await ctx.send("I'll remind you to " + reminder + " on " + args[0])
    else:
        await ctx.send("I need more info")

@bot.command()
async def generate1(ctx):
    response = bigram.torchGenerate()
    if response:
        await ctx.send(response)

@bot.command()
async def generate2(ctx):
    response = bigramModel2.torchGenerate()
    if response:
        await ctx.send(response)

bot.run(TOKEN)