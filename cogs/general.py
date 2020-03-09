import discord
from discord.ext import commands, tasks
import random
import settings
from itertools import cycle

status = cycle([[discord.ActivityType.playing, "as DRG because I'm an absolute bot lol"],
                [discord.ActivityType.watching, "Ex Machina"],
                [discord.ActivityType.listening, "to Megalovania at 300% speed"],
                [discord.ActivityType.watching, "a guide on E8S"],
                [discord.ActivityType.playing, "Celtic Heroes"],
                [discord.ActivityType.listening, "Joji - Run"],
                [discord.ActivityType.playing, "Destiny 2"],
                [discord.ActivityType.playing, "Kado Quest!"],
                [discord.ActivityType.playing, "Sub-Level Zero"],
                [discord.ActivityType.listening, "to a recording of McGill Typing"]])


class General(commands.Cog):

    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.update_status.start()

    # Dice Roll command
    @commands.command(name='Roll', help='Rolls x y sided dice. Example: !Roll 3 20')
    async def roll(self, ctx, number_of_dice: int, number_of_sides: int):
        # Validate input
        if number_of_dice > 20:
            await ctx.send("That's more dice than I can hold at once")
        elif number_of_sides > 1000:
            await ctx.send("Do you really need a die with that many sides?")
        elif number_of_dice == 0:
            await ctx.send(":clap: roll :clap: zero :clap: dice! :clap:")
        elif number_of_dice < 0:
            await ctx.send("I can't roll a negative amount of dice")
        elif number_of_sides < 2:
            await ctx.send("These dice probably need more sides to be functional")
        else:
            die_emoji = ':game_die:'
            total = 0
            dice = []
            for i in range(number_of_dice):
                dice_roll = random.choice(range(1, number_of_sides + 1))
                total += dice_roll
                dice.append(str(dice_roll))

            dice_text = (' ' + die_emoji).join(dice)
            await ctx.send(f'You rolled:\n{die_emoji}{dice_text}\nFor a total of :tada: ***{str(total)}*** :tada:')

    # Smug bot command
    @commands.command(name='Smug', help='Makes the bot smug')
    async def smug(self, ctx):
        smug_list = [
            '<:NicoSmug:519186875836268547>',
            '<:Smug:656595001748488192>',
            '<:smug2:519911675319549970>'
        ]
        # Send a random smug emoji from list
        await ctx.send(random.choice(smug_list))

    # Mock a message command
    @commands.command(name='Mock', help='Make a mockery of the last message')
    async def mock(self, ctx: discord.ext.commands.Context):
        # Get previous 2 messages
        messages = await ctx.history(limit=2).flatten()
        # Save the command message and the content of the message to mock
        message = messages[1].content
        request_message = messages[0]
        emoji_list = [
            '<:DisabledMegumin:519186875643068456>',
            '<:GalaxyBrain:617362965401960459>',
            '<:stinky:648972694209167377>'
        ]

        mocked_message = ''
        # Ensure the message was successfully received
        if message is not None:
            # Build a copy of the message with every other character uppercase
            flip_flop = False
            for char in message:
                if flip_flop:
                    mocked_message += char.upper()
                    flip_flop = not flip_flop
                else:
                    mocked_message += char.lower()
                    flip_flop = not flip_flop
            await ctx.send('>>> ' + mocked_message + ' ' + random.choice(emoji_list))
            await ctx.send('- Quote by idiot')
            # Delete the command message
            await request_message.delete()
        else:
            await ctx.send("Not sure what message I'm supposed to be mocking")

    # Command for checking the bots latency
    @commands.command(name="Ping", help="Checks the bots latency")
    async def ping(self, ctx):
        await ctx.send(f"{round(self.bot.latency * 1000)}ms")

    # Command for posting the bots github repo
    @commands.command(name="GitHub", help="Get a link to the bots GitHub Repo")
    async def github(self, ctx):
        await ctx.send("https://github.com/CrockerSloth/CrockBot")

    # Looping event for controlling bot status
    @tasks.loop(hours=1)
    async def update_status(self):
        if settings.debug:
            await self.bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.playing, name="DEBUG MODE"))
        else:
            chosen_status = next(status)
            await self.bot.change_presence(activity=discord.Activity(type=chosen_status[0], name=chosen_status[1]))

    @update_status.before_loop
    async def before_status_update(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(General(bot))
