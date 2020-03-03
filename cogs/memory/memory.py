import csv
from discord.ext import commands


class Memory(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='Learn', help='Lets you teach CrockBot a phrase. Example: !Learn greeting hello everyone!')
    async def learn(self, ctx, command, *, phrase):
        command = command.upper()
        command_found = False
        with open('cogs/memory/storage.csv', 'rt') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == command:
                    command_found = True
                    continue
            if command_found:
                await ctx.send("A command with that name already exists!")
        if not command_found:
            with open('cogs/memory/storage.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([command, phrase])
                await ctx.send(f"I have learnt a new command: {command}")

    @commands.command(name='Recall', help='Lets you recall a phrase CrockBot has learnt. Example: !Recall greeting')
    async def recall(self, ctx, command):
        command = command.upper()

        with open('cogs/memory/storage.csv', 'rt', encoding='utf-8') as file:
            reader = csv.reader(file)
            command_found = False
            for row in reader:
                if row is None:
                    continue
                if row[0] == command:
                    await ctx.send(row[1])
                    command_found = True
                    continue
            if not command_found:
                await ctx.send("I don't know that command!")

    @commands.command(name='Forget', help='Tells CrockBot to forget something. Example: !Forget greeting')
    async def forget(self, ctx, command):
        command = command.upper()

        cleaned_list = []
        command_found = False
        with open('cogs/memory/storage.csv', 'rt', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] != command:
                    cleaned_list.append([row[0], row[1]])
                else:
                    command_found = True

        if not command_found:
            await ctx.send('No command by that name exists')
        else:
            with open('cogs/memory/storage.csv', 'wt', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(cleaned_list)
                await ctx.send(f"I've forgotten the command: {command}")


def setup(bot):
    bot.add_cog(Memory(bot))
