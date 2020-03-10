import discord
from discord.ext import commands

# Create main help embed
help_embed = discord.Embed(title="Help Categories",
                           description="Use command !help [category] to see more info about a specific category",
                           color=0xf48c00)
help_embed.add_field(name="**General**", value="!help General", inline=False)
help_embed.add_field(name="**FFEvents**", value="!help FFEvents", inline=False)
help_embed.add_field(name="**Memory**", value="!help Memory", inline=False)

# Create general help embed
general_embed = discord.Embed(title="General Commands",
                              description="This category has all the commands that don't fit in a specific section",
                              color=0xf48c00)
general_embed.add_field(name="**!Vibe**",
                        value="Assigns you a vibe for the day or shows your vibe if you already have one. Vibes reset everyday",
                        inline=False)
general_embed.add_field(name="**!Mock**",
                        value="Has the bot repeat the previous comment in a mocking manner",
                        inline=False)
general_embed.add_field(name="**!Smug**",
                        value="Makes the bot feel very smug",
                        inline=False)
general_embed.add_field(name="**!Ping**",
                        value="Checks the bots latency",
                        inline=False)
general_embed.add_field(name="**!Roll**",
                        value="Rolls some dice. Example: *!roll 5 20* will roll 5 20 sided dice.",
                        inline=False)
general_embed.add_field(name="**!GitHub**",
                        value="Links the bots GitHub Repo",
                        inline=False)

# Create memory help embed
memory_embed = discord.Embed(title="Memory Commands",
                             description="This category contains all the commands related to teaching the bot new phrases",
                             color=0xf48c00)
memory_embed.add_field(name="**!Learn**",
                       value="Lets you teach the bot a phrase. Example: *!learn greeting Hello!* will teach the bot the phrase 'Hello!' and the command 'greeting'",
                       inline=False)
memory_embed.add_field(name="**!Recall**",
                       value="Tells the bot to recall a phrase it has learnt. Example *!recall greeting* will have the bot say 'hello!'",
                       inline=False)
memory_embed.add_field(name="**!Forget**",
                       value="Makes the bot forget a phrase it has learnt. Example *!forget greeting* will make the bot forget the command 'greeting'",
                       inline=False)

# Create ffevent help embed
ffevents_embed = discord.Embed(title="FFEvents Commands",
                               description="This category contains all the commands related to organising Final Fantasy 14 events",
                               color=0xf48c00)
ffevents_embed.add_field(name="**!FFEvent**",
                         value="Tells the bot to create a new event. Example:\n*!ffevent*\n*Event*\n*Description of event*\n*2020/03/20 7:00PM*",
                         inline=False)
ffevents_embed.add_field(name="**!FFList**",
                         value="Tells the bot to send a list of all upcoming events and how long until the event",
                         inline=False)
ffevents_embed.add_field(name="**!FFCancel**",
                         value="Tells the bot to cancel an existing event. Example: *!ffcancel Event*",
                         inline=False)


class Help(commands.Cog):

    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, *, category: str = None):
        if not category:
            await ctx.send(embed=help_embed)
        elif category.upper() == 'GENERAL':
            await ctx.send(embed=general_embed)
        elif category.upper() == 'FFEVENTS':
            await ctx.send(embed=ffevents_embed)
        elif category.upper() == 'MEMORY':
            await ctx.send(embed=memory_embed)
        else:
            await ctx.send("That category does not exist")


def setup(bot):
    bot.add_cog(Help(bot))
