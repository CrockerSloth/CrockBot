import discord
from discord.ext import commands
import random


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='Roll', help='Rolls x y sided dice. Example: !Roll 3 20')
    async def roll(self, ctx, number_of_dice: int, number_of_sides: int):
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

    @commands.command(name='Smug', help='Makes the bot smug')
    async def smug(self, ctx):
        smug_list = [
            '<:NicoSmug:519186875836268547>',
            '<:Smug:656595001748488192>',
            '<:smug2:519911675319549970>'
        ]
        await ctx.send(random.choice(smug_list))

    @commands.command(name='Mock', help='Make a mockery of the last message')
    async def mock(self, ctx: discord.ext.commands.Context):
        messages = await ctx.history(limit=2).flatten()
        message = messages[1].content
        request_message = messages[0]
        emoji_list = [
            '<:DisabledMegumin:519186875643068456>',
            '<:GalaxyBrain:617362965401960459>',
            '<:stinky:648972694209167377>'
        ]
        mocked_message = ''
        if message is not None:
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
            await request_message.delete()
        else:
            await ctx.send("Not sure what message I'm supposed to be mocking")


def setup(bot):
    bot.add_cog(General(bot))

