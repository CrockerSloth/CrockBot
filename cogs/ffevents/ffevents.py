import maya
import pickle
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import pytz

# Constants for emoji
DPS_EMOJI = '<:dps:684082812579741707>'
TANK_EMOJI = '<:tank:684082813305487435>'
HEALER_EMOJI = '<:healer:684082813783506981>'

# Tag for raid team
TAG = '<@&533285899597774858>'

watched_raids = {}

# Open the raid file or create a new one if none exist
try:
    with open('cogs/ffevents/raids.pickle', 'rb') as file:
        watched_raids = pickle.load(file)
except:
    with open('cogs/ffevents/raids.pickle', 'wb') as file:
        pickle.dump(watched_raids, file)


# Build a discord rich embed for the raid event
def build_raid_embed(raid):
    readable_date = str(raid['datetime']) + '\n' + raid['datetime'].slang_time()
    embed = discord.Embed(title=raid['info']['title'], description=raid['info']['description'], color=0x2bbb00)
    embed.add_field(name="Time", value=readable_date, inline=False)
    embed.add_field(name="Tanks", value=raid['tank'], inline=False)
    embed.add_field(name="Healers", value=raid['healer'], inline=False)
    embed.add_field(name="DPS", value=raid['dps'], inline=False)
    return embed


# Compare the reaction emoji to the emoji consts to find out what type of reaction was used
def check_raid_emoji(payload):
    emoji_type = ''
    wrong_emoji = False
    if str(payload.emoji) == TANK_EMOJI:
        emoji_type = 'tank'
    elif str(payload.emoji) == HEALER_EMOJI:
        emoji_type = 'healer'
    elif str(payload.emoji) == DPS_EMOJI:
        emoji_type = 'dps'
    else:
        wrong_emoji = True
    return [wrong_emoji, emoji_type]


class FFEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.watched_raids = watched_raids
        self.check_watched_raids.start()

    # Save the new list to the raid file and update the rich embed
    async def update_rich_embed(self, payload):
        raid = self.watched_raids[payload.message_id]
        embed = build_raid_embed(raid)
        channel = self.bot.get_channel(payload.channel_id)
        raid_message = await channel.fetch_message(payload.message_id)
        await raid_message.edit(content=TAG, embed=embed)

    # Command that listens for reactions being add to messages on all channels bot can see
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Make sure the reaction was added to a raid that the bot is currently tracking
        if payload.message_id in self.watched_raids and not payload.member == self.bot.user:

            # See if the reaction emoji matches one of the classes
            check_results = check_raid_emoji(payload)
            wrong_emoji = check_results[0]
            emoji_type = check_results[1]

            # Check if the emoji returned a match and the user who reacted isn't already in the matching list
            if not wrong_emoji and payload.member.name not in self.watched_raids[payload.message_id][emoji_type]:
                # Add that the user who reacted to the appropriate tracked raid list
                self.watched_raids[payload.message_id][emoji_type].append(str(payload.member))

                with open('cogs/ffevents/raids.pickle', 'wb') as f:
                    pickle.dump(self.watched_raids, f)
                await self.update_rich_embed(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        user = self.bot.get_user(payload.user_id)
        # Make sure the reaction was removed from a raid that the bot is currently tracking
        if payload.message_id in self.watched_raids and not user == self.bot.user:

            # Check if the emoji was one of the linked emoji
            check_results = check_raid_emoji(payload)
            wrong_emoji = check_results[0]
            emoji_type = check_results[1]

            # Check if the emoji returned a match and the user who removed is in the matching list
            if not wrong_emoji and user.name not in self.watched_raids[payload.message_id][emoji_type]:
                # Remove the user from the matching list
                self.watched_raids[payload.message_id][emoji_type].remove(str(user))

                with open('cogs/ffevents/raids.pickle', 'wb') as f:
                    pickle.dump(self.watched_raids, f)
                await self.update_rich_embed(payload)

    # Command for setting up a new final fantasy event
    @commands.command(name='FFevent',
                      help='Lets you plan a final fantasy 14 event. '
                           'Example: !FFevent title | description | date and time')
    async def ffevent(self, ctx: commands.Context, *, info):
        # Check the user entered the expected amount of inputs
        info_list = info.split('\n')
        if len(info_list) == 3:
            # Make sure the event name is unique (for the purpose ot the cancel command)
            for raid in self.watched_raids.values():
                if raid['info']['title'] == info_list[0]:
                    await ctx.send("An event with that name already exists")
                    return

            # Attempt to parse the users date time
            try:
                parsed_date = maya.when(info_list[2], timezone="GMT")
            except:
                await ctx.send("I didn't understand the date and time you entered")
                return

            # Create raid info
            raid = {'tank': [],
                    'healer': [],
                    'dps': [],
                    'info': {'title': info_list[0],
                             'description': info_list[1]},
                    'datetime': parsed_date,
                    'channel': None,
                    'reminded': False}

            # Create a rich embed and post it
            embed = build_raid_embed(raid)
            message = await ctx.send(content=TAG, embed=embed)

            # Update the channel id in the raid now the message is sent
            raid['channel'] = message.channel.id

            # Add the new raid to the tracked raids list and save the file
            self.watched_raids.update({message.id: raid})
            with open('cogs/ffevents/raids.pickle', 'wb') as f:
                pickle.dump(self.watched_raids, f)

            # Add the linked emoji reactions to the message and pin the message to the channel
            await message.add_reaction(TANK_EMOJI)
            await message.add_reaction(HEALER_EMOJI)
            await message.add_reaction(DPS_EMOJI)
            await message.pin()
        else:
            await ctx.send("You made a mistake. Make sure to enter a title, description and time on separate lines")

    # Command for listing all currently tracked raids
    @commands.command(name='FFlist', help='Lists all the FFXIV events currently being tracked')
    async def fflist(self, ctx):
        # Check if there are any upcoming events in the list
        if len(self.watched_raids) == 0:
            await ctx.send("There are no upcoming FFXIV events")
        else:
            message = '***These are the upcoming ff events***\n'
            for raid in self.watched_raids.values():
                readable_date = str(raid['datetime']) + ' ' + raid['datetime'].slang_time()
                message += raid['info']['title'] + ' - *' + readable_date + '*\n'
            await ctx.send(message)

    # Event for cancelling a tracked raid event
    @commands.command(name='FFcancel', help='Cancels an FFXIV event. Example: !ffcancel raid')
    async def ffcancel(self, ctx, *, title):
        # Check raid list for matching raid title
        for raid in self.watched_raids.items():
            if raid[1]['info']['title'] == title:
                # Delete message linked to matching raid
                channel = self.bot.get_channel(raid[1]['channel'])
                raid_message = await channel.fetch_message(raid[0])
                await raid_message.delete()

                # Remove raid from tracked messages list and save file
                del self.watched_raids[raid[0]]
                with open('cogs/ffevents/raids.pickle', 'wb') as f:
                    pickle.dump(self.watched_raids, f)

                await ctx.send("I have cancelled the event: " + title)
        await ctx.send("I couldn't find a matching event")

    # Loop for checking raids in the tracking file
    @tasks.loop(minutes=1)
    async def check_watched_raids(self):
        # Check if tracked raid list is empty
        if len(self.watched_raids) == 0:
            return
        else:
            for raid in self.watched_raids.items():
                now = datetime.now(pytz.timezone('GMT'))
                delta = raid[1]['datetime'].datetime() - now
                cancel_delta = timedelta(hours=-1)
                remind_delta = timedelta(hours=3, minutes=5)
                if raid[1]['reminded'] and delta < cancel_delta:
                    # Cancel the raid
                    # Delete message linked to matching raid
                    channel = self.bot.get_channel(raid[1]['channel'])
                    raid_message = await channel.fetch_message(raid[0])
                    await raid_message.delete()

                    # Remove raid from tracked messages list and save file
                    del self.watched_raids[raid[0]]
                    with open('cogs/ffevents/raids.pickle', 'wb') as f:
                        pickle.dump(self.watched_raids, f)

                elif not raid[1]['reminded'] and delta < remind_delta:
                    # Remind people of the raid
                    channel = self.bot.get_channel(raid[1]['channel'])
                    await channel.send(
                        TAG + '\n**' + raid[1]['info']['title'] + '** ' + raid[1]['datetime'].slang_time())

                    # Mark raid as having sent a reminder
                    raid[1]['reminded'] = True
                    # Save raid file
                    with open('cogs/ffevents/raids.pickle', 'wb') as f:
                        pickle.dump(self.watched_raids, f)

                # Update time on rich embed
                channel = self.bot.get_channel(raid[1]['channel'])
                raid_message = await channel.fetch_message(raid[0])
                embed = build_raid_embed(raid[1])
                await raid_message.edit(content=TAG, embed=embed)

    @check_watched_raids.before_loop
    async def before_check_watched_raids(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(FFEvents(bot))
