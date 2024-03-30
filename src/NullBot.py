# bot.py
import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == 'hi nullbot' or message.content.lower() == 'hey nullbot' or message.content.lower() == 'hello nullbot':
        response = 'Hey'
        await message.channel.send(response)

client.run(TOKEN)