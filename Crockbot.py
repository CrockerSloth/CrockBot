import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from itertools import cycle
import settings

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Set bot command prefix and load cogs
bot = commands.Bot(command_prefix='!', case_insensitive=True)
bot.remove_command('help')
bot.load_extension('cogs.general.general')
bot.load_extension('cogs.memory.memory')
bot.load_extension('cogs.ffevents.ffevents')
bot.load_extension('cogs.help')


# Event that fires when bot connects to discord
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


# Exception handler for commands missing arguments
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('You forgot to include some important information with that command')


# Event that that fires when a new message is received
@bot.event
async def on_message(message):
    # Capture message if the message is a direct message
    if message.author != bot.user and message.guild is None:
        await message.channel.send("Please don't message me. I'm not supposed to be alone with people")
    # Otherwise, check for debug mode and then let the messages through.
    else:
        if message.author != bot.user and settings.debug:
            if message.author.id == settings.approved_user:
                await bot.process_commands(message)
        else:
            await bot.process_commands(message)


bot.run(token)
