from discord.ext import commands, tasks
from discord.utils import get
from datetime import datetime, timedelta
import discord
import pickle
import random
import csv
import asyncio

# Settings
rarity_increase = 15

# Role id's for rarity
empty_role = 688907869416063034
broken_role = 688909250415820886
common_role = 688909378891415583
uncommon_role = 688909639747895488
rare_role = 688909739999887456
epic_role = 688909828395106403
legendary_role = 688910253202341898
elder_role = 688910352536043544
corrupt_role = 688910395238514708
ascended_role = 689499862102048919

all_roles = [empty_role,
             broken_role,
             common_role,
             uncommon_role,
             rare_role,
             epic_role,
             legendary_role,
             elder_role,
             corrupt_role,
             ascended_role]

role_colours = [0x575757,
                0x8d8d8d,
                0xcecece,
                0x009b03,
                0x316ca0,
                0xbd0000,
                0xffd900,
                0x932bb6,
                0x050505,
                0xf19dcf]

role_names = ['Empty',
              'Broken',
              'Common',
              'Uncommon',
              'Rare',
              'Epic',
              'Legendary',
              'Elder',
              'Corrupt',
              'Ascended']

# Emoji's used in embeds
skull_emoji = '💀'
crown_emoji = '👑'
higher_emoji = '☝️'
lower_emoji = '👇'
gem_emoji = '💎'
right_emoji = '➡️'

looting = {}
looters = {}

# Open looting file or create one if none exist
try:
    with open('cogs/loot/looting.pickle', 'rb') as file:
        looting = pickle.load(file)
except:
    with open('cogs/loot/looting.pickle', 'wb') as file:
        pickle.dump(looting, file)

# Open looters file or create one if none exist
try:
    with open('cogs/loot/looters.pickle', 'rb') as file:
        looters = pickle.load(file)
except:
    with open('cogs/loot/looters.pickle', 'wb') as file:
        pickle.dump(looters, file)


def generate_start_embed(author):
    start_embed = discord.Embed(title="The Vaults of Atziri",
                                description="You stand before the vaults of Atziri. Inscribed into the stone pillars around the room are instructions left by the Vaal. *'Play the Queen's game or take what you're given'*. The front of the vault has two movable stone slabs.")
    start_embed.set_author(name=author)
    start_embed.add_field(name="💀", value="Play the Queen's game", inline=True)
    start_embed.add_field(name="👑", value="Take what you're given", inline=True)
    return start_embed


def generate_item_embed(author, item_name, rarity, colour, success, current_roll):
    # Change text if they failed the game
    if success:
        description = "You reach your hand through an opening in the vault door and grasp the first item you touch. Pulling it out, you see that you have found..."
    else:
        description = f"The Boulder rolled a {current_roll}\nYou failed the queen's game and forfeit your item rarity!\nYou reach your hand through an opening in the vault door and grasp the first item you touch. Pulling it out, you see that you have found..."

    embed = discord.Embed(title="The Vaults of Atziri",
                          description=description,
                          color=colour)
    embed.set_author(name=author)
    embed.add_field(name=role_names[rarity], value=f"**💎 {item_name} 💎**", inline=True)
    return embed


def generate_game_embed(author, current_roll, current_rarity, next_rarity, success):
    if success:
        description = 'Success!\nAnother 10 sided boulder with red numbers etched on each side rolls to the centre of the room.'
    else:
        description = 'A 10 sided boulder with red numbers etched on each side rolls to the centre of the room. There are 3 levers on the vault door.'
    embed = discord.Embed(title="The Vaults of Atziri",
                          description=description,
                          color=0x000000)
    embed.add_field(value=f"The boulder rests on a **{current_roll}**",
                    name=f"{current_rarity}% Item Rarity {right_emoji} {next_rarity}% Item Rarity",
                    inline=False)
    embed.set_author(name=author)
    embed.add_field(name="Commands",
                    value="☝️ Guess that the next boulder will roll higher!\n\n👇 Guess that the next boulder will roll lower!\n\n💎 Claim your prize",
                    inline=False)
    return embed


def generate_item_name():
    # Select random item and suffix
    with open('cogs/loot/items.csv', 'rt', encoding='utf-8') as f:
        # Select an item
        reader = csv.reader(f)
        chosen_item = random.choice(list(reader))
    with open('cogs/loot/suffix.csv', 'rt', encoding='utf-8') as f:
        # Select an item
        reader = csv.reader(f)
        chosen_suffix = random.choice(list(reader))
    return chosen_item[0] + ' ' + chosen_suffix[0]


def generate_item_rarity(item_rarity):
    # if user failed the game. ensure a broken item is created
    if item_rarity == 0:
        return 1

    # Create a max roll range by doing the sum of all rarity brackets
    probability_ratio = 2
    roll_range_max = 1
    current_tier_size = 1
    for i in range(1, len(all_roles) - 2):
        current_tier_size = current_tier_size * probability_ratio
        roll_range_max += current_tier_size

    # Make sure item rarity never goes too high
    if item_rarity >= roll_range_max:
        item_rarity = roll_range_max - 1

    # roll a random value and subtract each rarity bracket until the value is below zero to find the rarity tier
    random_roll = random.randrange(0, roll_range_max - item_rarity)
    current_tier = len(all_roles) - 1
    current_tier_bracket = 1
    for i in range(0, len(all_roles) - 2):
        random_roll -= current_tier_bracket
        if random_roll < 0:
            return current_tier
        current_tier_bracket = current_tier_bracket * probability_ratio
        current_tier -= 1

    # If something goes wrong, return common and warn terminal
    print("item rarity role failed to find result")
    return 2


class Loot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.looting = looting
        self.looters = looters

        self.reset_looting.start()

    async def award_item(self, payload, message_id, success, current_roll=0):
        # Remove user from looting list
        del self.looting[payload.message_id]

        with open('cogs/loot/looting.pickle', 'wb') as f:
            pickle.dump(self.looting, f)

        # Generate an item
        item_name = generate_item_name()
        rarity = generate_item_rarity(self.looting[message_id][2])
        colour = role_colours[rarity]

        # Assign the item role
        new_role = await payload.member.guild.create_role(name=item_name,
                                                          colour=discord.Colour(colour),
                                                          mentionable=True)
        await payload.member.add_roles(new_role)

        # Assign the rarity role
        rarity_role = get(payload.member.guild.roles, id=all_roles[rarity])
        await payload.member.add_roles(rarity_role)

        # Change role position in list
        position = len(payload.member.guild.roles) - len(all_roles) - 3
        await new_role.edit(position=position)

        # Remove empty role
        role = get(payload.member.guild.roles, id=all_roles[0])
        await payload.member.remove_roles(role)

        # Update message and remove reactions
        item_embed = generate_item_embed(str(payload.member), item_name, rarity, colour, success, current_roll)
        channel = self.bot.get_channel(payload.channel_id)
        loot_message = await channel.fetch_message(payload.message_id)
        await loot_message.edit(embed=item_embed)
        await loot_message.clear_reactions()

        # Update users looter value for the day
        self.looters[str(payload.member)] = [True, new_role.id, rarity]

        with open('cogs/loot/looters.pickle', 'wb') as f:
            pickle.dump(self.looters, f)

    async def play_game(self, payload, message_id, current_roll, success=False):
        # Set update looting settings
        self.looting[payload.message_id][4] = True
        self.looting[payload.message_id][3] = current_roll

        with open('cogs/loot/looting.pickle', 'wb') as f:
            pickle.dump(self.looting, f)

        # Update message and remove reactions
        next_rarity = self.looting[payload.message_id][2] + rarity_increase
        game_embed = generate_game_embed(str(payload.member),
                                         current_roll,
                                         self.looting[payload.message_id][2],
                                         next_rarity,
                                         success)
        channel = self.bot.get_channel(payload.channel_id)
        game_message = await channel.fetch_message(payload.message_id)
        await game_message.edit(embed=game_embed)
        await game_message.clear_reactions()
        await game_message.add_reaction(higher_emoji)
        await game_message.add_reaction(lower_emoji)
        await game_message.add_reaction(gem_emoji)

    @commands.command(name='loot')
    async def loot(self, ctx):
        author = ctx.message.author.name + '#' + ctx.message.author.discriminator
        # Check if user has already looted or is already looting the vaults
        looting_authors = []
        for value in self.looting.values():
            looting_authors.append(value[0])
        if author in looting_authors:
            await ctx.send('You are already looting the Vaults!')
            return
        if author in self.looters:
            if self.looters[author][0]:
                await ctx.send('You looted the vaults already today. Come back tomorrow!')
                return

        # Remove current item
        if author in self.looters:
            # Delete the user's current item role and remove their rarity
            rarity_role = get(ctx.guild.roles, id=all_roles[self.looters[author][2]])
            await ctx.author.remove_roles(rarity_role)
            current_role = get(ctx.guild.roles, id=self.looters[author][1])
            await current_role.delete()
        # Add the empty role
        role = get(ctx.guild.roles, id=empty_role)
        await ctx.author.add_roles(role)

        # create the start embed and add the option reactions
        start_embed = generate_start_embed(author)
        message = await ctx.send(embed=start_embed)
        await message.add_reaction(skull_emoji)
        await message.add_reaction(crown_emoji)

        # Add new looting to looting list and save to file
        self.looting[message.id] = [author, message.channel.id, 5, 0, False]
        with open('cogs/loot/looting.pickle', 'wb') as f:
            pickle.dump(self.looting, f)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id in self.looting:
            if self.looting[payload.message_id][0] == str(payload.member):
                current_looting_id = payload.message_id
                if not self.looting[payload.message_id][4]:
                    if payload.emoji.name == skull_emoji:
                        # Logic for playing the queen's game
                        # Roll boulder
                        current_roll = random.randint(1, 10)
                        await self.play_game(payload, current_looting_id, current_roll)
                        return
                    elif payload.emoji.name == crown_emoji:
                        # Logic for taking an item without gambling
                        await self.award_item(payload, current_looting_id, True)
                        return
                else:
                    if payload.emoji.name == higher_emoji:
                        # Roll boulder until a new roll above or below the old roll is chosen
                        previous_roll = self.looting[payload.message_id][3]
                        current_roll = random.randint(1, 10)
                        while current_roll == previous_roll:
                            current_roll = random.randint(1, 10)
                        if current_roll > previous_roll:
                            # success! onto next round!
                            self.looting[payload.message_id][3] = current_roll
                            self.looting[payload.message_id][2] += rarity_increase
                            await self.play_game(payload, current_looting_id, current_roll, True)
                        else:
                            # Failure lose item rarity and give item
                            self.looting[payload.message_id][2] = 0
                            await self.award_item(payload, current_looting_id, False, current_roll)
                    elif payload.emoji.name == lower_emoji:
                        # Roll boulder until a new roll above or below the old roll is chosen
                        previous_roll = self.looting[payload.message_id][3]
                        current_roll = random.randint(1, 10)
                        while current_roll == previous_roll:
                            current_roll = random.randint(1, 10)
                        if current_roll < previous_roll:
                            # success! onto next round!
                            self.looting[payload.message_id][3] = current_roll
                            self.looting[payload.message_id][2] += rarity_increase
                            await self.play_game(payload, current_looting_id, current_roll, True)
                        else:
                            # Failure lose item rarity and give item
                            self.looting[payload.message_id][2] = 0
                            await self.award_item(payload, current_looting_id, False, current_roll)
                    elif payload.emoji.name == gem_emoji:
                        await self.award_item(payload, current_looting_id, True)
                        return

    # Looping event for resetting user loot ever day.
    @tasks.loop(hours=24)
    async def reset_looting(self):
        for looter in self.looters.keys():
            self.looters[looter][0] = False

        with open('cogs/loot/looters.pickle', 'wb') as f:
            pickle.dump(self.looters, f)

    @reset_looting.before_loop
    async def before_reset_looting(self):
        # Wait until the desired reset time before starting the reset loop
        await self.bot.wait_until_ready()
        now = datetime.utcnow()
        reset = now.replace(day=now.day, hour=15, minute=0, second=0, microsecond=0)
        delta = reset - now
        fixed_delta = timedelta(seconds=delta.seconds)
        pause = fixed_delta.total_seconds()
        await asyncio.sleep(pause)


def setup(bot):
    bot.add_cog(Loot(bot))
