import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!', case_insensitive=True)
bot.load_extension('cogs.general')
bot.load_extension('cogs.memory.memory')
bot.load_extension('cogs.ffevents.ffevents')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="Ex Machina"))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('You forgot to include some important information with that command')


@bot.event
async def on_message(message):
    if message.author != bot.user and message.guild is None:
        await message.channel.send("Please don't message me. I'm not supposed to be alone with people")
    else:
        await bot.process_commands(message)


bot.run(token)
