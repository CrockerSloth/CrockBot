import maya
import pickle
import discord
from discord.ext import commands

DPS_EMOJI = '<:dps:684082812579741707>'
TANK_EMOJI = '<:tank:684082813305487435>'
HEALER_EMOJI = '<:healer:684082813783506981>'

TAG = '<@&533285899597774858>'

watched_raids = {}

try:
    with open('cogs/ffevents/raids.pickle', 'rb') as file:
        watched_raids = pickle.load(file)
except:
    with open('cogs/ffevents/raids.pickle', 'wb') as f:
        pickle.dump({}, f)


def build_raid_embed(tanks, healers, dps, info):
    embed = discord.Embed(title=info[0], description=info[1], color=0x2bbb00)
    embed.add_field(name="Time", value=info[2], inline=False)
    embed.add_field(name="Tanks", value=tanks, inline=False)
    embed.add_field(name="Healers", value=healers, inline=False)
    embed.add_field(name="DPS", value=dps, inline=False)
    return embed


def check_raid_emoji(payload):
    raid_index = 0
    wrong_emoji = False
    if str(payload.emoji) == TANK_EMOJI:
        raid_index = 0
    elif str(payload.emoji) == HEALER_EMOJI:
        raid_index = 1
    elif str(payload.emoji) == DPS_EMOJI:
        raid_index = 2
    else:
        wrong_emoji = True
    return [wrong_emoji, raid_index]


class FFEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.watched_raids = watched_raids

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id in self.watched_raids and not payload.member == self.bot.user:

            check_results = check_raid_emoji(payload)
            wrong_emoji = check_results[0]
            raid_index = check_results[1]

            if not wrong_emoji and payload.member.name not in self.watched_raids[payload.message_id][raid_index]:
                self.watched_raids[payload.message_id][raid_index].append(str(payload.member))

                with open('cogs/ffevents/raids.pickle', 'wb') as f:
                    pickle.dump(self.watched_raids, f)

                raid = self.watched_raids[payload.message_id]
                embed = build_raid_embed(raid[0], raid[1], raid[2], raid[3])
                channel = self.bot.get_channel(payload.channel_id)
                raid_message = await channel.fetch_message(payload.message_id)
                await raid_message.edit(content=TAG, embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        user = self.bot.get_user(payload.user_id)
        if payload.message_id in self.watched_raids and not user == self.bot.user:

            check_results = check_raid_emoji(payload)
            wrong_emoji = check_results[0]
            raid_index = check_results[1]

            if not wrong_emoji and user.name not in self.watched_raids[payload.message_id][raid_index]:
                self.watched_raids[payload.message_id][raid_index].remove(str(user))

                with open('cogs/ffevents/raids.pickle', 'wb') as f:
                    pickle.dump(self.watched_raids, f)

                raid = self.watched_raids[payload.message_id]
                embed = build_raid_embed(raid[0], raid[1], raid[2], raid[3])
                channel = self.bot.get_channel(payload.channel_id)
                raid_message = await channel.fetch_message(payload.message_id)
                await raid_message.edit(content=TAG, embed=embed)

    @commands.command(name='FFevent',
                      help='Lets you plan a final fantasy 14 event. Example: !FFevent title | description | date and time')
    async def ffevent(self, ctx: commands.Context, *, info):
        info_list = info.split('\n')
        if len(info_list) == 3:
            for raid in self.watched_raids.values():
                if raid[3][0] == info_list[0]:
                    await ctx.send("An event with that name already exists")
                    return

            try:
                parsed_date = (maya.parse(info_list[2]).datetime())
                info_list[2] = str(parsed_date.date()) + ' ' + str(parsed_date.time())
            except:
                await ctx.send("I didn't understand the date and time you entered")
                return
            embed = build_raid_embed([], [], [], info_list)
            message = await ctx.send(content=TAG, embed=embed)
            self.watched_raids.update({message.id: [[], [], [], info_list, message.channel.id]})

            with open('cogs/ffevents/raids.pickle', 'wb') as f:
                pickle.dump(self.watched_raids, f)

            await message.add_reaction(TANK_EMOJI)
            await message.add_reaction(HEALER_EMOJI)
            await message.add_reaction(DPS_EMOJI)
            await message.pin()
        else:
            await ctx.send("You made a mistake. Make sure to enter a title, description and time on separate lines")

    @commands.command(name='FFlist', help='Lists all the FFXIV events currently being tracked')
    async def fflist(self, ctx):
        if len(self.watched_raids) == 0:
            await ctx.send("There are no upcoming FFXIV events")
        else:
            message = '***These are the upcoming ff events***\n'
            for raid in self.watched_raids.values():
                message += raid[3][0] + ' - *' + raid[3][2] + '*\n'
            await ctx.send(message)

    @commands.command(name='FFcancel', help='Cancels an FFXIV event. Example: !ffcancel raid')
    async def ffcancel(self, ctx, *, title):
        for raid in self.watched_raids.items():
            if raid[1][3][0] == title:
                channel = self.bot.get_channel(raid[1][4])
                raid_message = await channel.fetch_message(raid[0])
                await raid_message.delete()

                del self.watched_raids[raid[0]]

                with open('cogs/ffevents/raids.pickle', 'wb') as f:
                    pickle.dump(self.watched_raids, f)

                await ctx.send("I have cancelled the event: " + title)
        await ctx.send("I couldn't find a matching event")


def setup(bot):
    bot.add_cog(FFEvents(bot))
