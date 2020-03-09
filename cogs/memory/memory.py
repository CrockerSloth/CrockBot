import csv
from discord.ext import commands


class Memory(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Command for teaching the bot new commands
    @commands.command(name='Learn', help='Lets you teach CrockBot a phrase. Example: !Learn greeting hello everyone!')
    async def learn(self, ctx, command, *, phrase):
        # Convert command to upper case to make inout case insensitive
        command = command.upper()
        command_found = False

        # Open the bots storage file and check if the command already exists
        # UTF-8 encoding is used to ensure emoji are properly retained
        with open('cogs/memory/storage.csv', 'rt', encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == command:
                    command_found = True
                    continue
            if command_found:
                await ctx.send("A command with that name already exists!")
        # If the command is unique then store the command and phrase in the storage.csv
        if not command_found:
            with open('cogs/memory/storage.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([command, phrase])
                await ctx.send(f"I have learnt a new command: {command}")

    # Command for recalling a learnt command
    @commands.command(name='Recall', help='Lets you recall a phrase CrockBot has learnt. Example: !Recall greeting')
    async def recall(self, ctx, command):
        # Make command case insensitive
        command = command.upper()

        # Open storage file and search for command
        with open('cogs/memory/storage.csv', 'rt', encoding='utf-8') as file:
            reader = csv.reader(file)
            command_found = False
            for row in reader:
                # Ignore blank rows (Last row is always blank)
                if row is None:
                    continue
                # Once command is found have the bot send the linked phrase
                if row[0] == command:
                    await ctx.send(row[1])
                    command_found = True
                    continue
            # Warn user if a command cannot be found
            if not command_found:
                await ctx.send("I don't know that command!")

    # Command to delete commands from storage file
    @commands.command(name='Forget', help='Tells CrockBot to forget something. Example: !Forget greeting')
    async def forget(self, ctx, command):
        # Make command case insensitive
        command = command.upper()

        cleaned_list = []
        command_found = False
        # Create a copy of the csv list whilst checking for and removing the user command
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
            # Write over the csv file with the cleaned list
            with open('cogs/memory/storage.csv', 'wt', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(cleaned_list)
                await ctx.send(f"I've forgotten the command: {command}")


def setup(bot):
    bot.add_cog(Memory(bot))
