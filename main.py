##
# main.py
# Date: 27/05/2023
# Authors: JJ Elwood and Ryan Gordon
# :D

import discord
import random
import asyncio
from discord.ext import commands
import os
from enum import Enum


class Modes(Enum):
    """
    Current mode of the bot.

    Annoy everyone - pings you if you don't ping the target.
    Reminder - pings the target at random intervals.
    Random pings - has a 2% chance of pinging you if you don't ping the target
        with every message.
    """
    ANNOY_EVERYONE = 0
    REMINDER = 1
    RANDOM_PINGS = 2
    PRIDE_MONTH = 3


# Server information.
USER_IDS = {"Ryan": 877750921474502717, "Sofia": 424719746869624865}
CHANNEL_IDS = {
    "General": 1084971815996227765,
    "Suggestions": 1083873072785936495,
    "Announcements": 1083867162046890055,
    "Testing": 1113427709616463922
}

# Super important constants that determine this bot's fate.
TARGET_ID = USER_IDS["Ryan"]
MODE = Modes.PRIDE_MONTH
PRIDE_MONTH_STARTING = False

# Other also important constants.
FEEDBACK_MESSAGES = [
    f"You've been naughty :index_pointing_at_the_viewer: - grabbing "
    f"<@{TARGET_ID}> rn",
    "404 Ping Not Found", f"Smhhh, no ping for <@{TARGET_ID}> :(((",
    f"Shouldn't say such things without <@{TARGET_ID}> :pensive:",
    "Nuh uh, that's not the kind of language we use in here",
    f"Check the new admin policy re <@{TARGET_ID}>",
    "<:angery:1092655340727849041>"
]

PRIDE_MESSAGES = [
    "<:redguy:1106525937136324688> <:orangeguy:1106525377708429352> "
    "<:yellowguy:1106524765977583657> <:greenguy:1095161810870607953> "
    "<:blueguy:1095161113773101229> <:pinkguy:1106523189238050886> "
    "<:purpleguy:1106524177663528990>"
]

MIN_TIME = 60 * 60 * 3
MAX_TIME = 60 * 60 * 30

# Set up intents and bot.
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True
#intents.message_content = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents,
)

recent_channel = None
sleep_time = 0


@bot.event
async def on_ready():
    global sleep_time
    print(f'Bot is ready. Logged in as {bot.user.name}')

    await bot.get_channel(CHANNEL_IDS["Testing"]).send("The bot has started")

    if MODE not in (Modes.REMINDER, Modes.PRIDE_MONTH):
        return

    if MODE == Modes.PRIDE_MONTH and PRIDE_MONTH_STARTING:
        await bot.get_channel(CHANNEL_IDS["Announcements"]).send(
            f"{PRIDE_MESSAGES[0]} Pride month is here :D "
            f"{' '.join(list(reversed(PRIDE_MESSAGES[0].split())))}")

    while True:
        sleep_time = random.randint(MIN_TIME, MAX_TIME)
        await asyncio.sleep(sleep_time)
        match MODE:
            case Modes.REMINDER:
                if recent_channel is not None:
                    await recent_channel.send(
                        f"<@{TARGET_ID}> Here's your random reminder :)")
            case Modes.PRIDE_MONTH:
                await bot.get_channel(CHANNEL_IDS["General"]).send(
                    random.choice(PRIDE_MESSAGES))
            case _:
                pass


@bot.event
async def on_message(message):
    global recent_channel

    match MODE:
        case Modes.ANNOY_EVERYONE:
            if TARGET_ID not in [u.id for u in message.mentions]:
                await message.channel.send(
                    f"{message.author.mention} "
                    f"{random.choice(FEEDBACK_MESSAGES)}")
        case Modes.REMINDER:
            recent_channel = message.channel
        case Modes.RANDOM_PINGS:
            if random.randint(1, 100) > 98:
                if TARGET_ID not in [u.id for u in message.mentions]:
                    await message.channel.send(
                        f"{message.author.mention} "
                        f"{random.choice(FEEDBACK_MESSAGES)}")
        case _:
            pass

    await bot.process_commands(message)


@bot.event
async def on_message_edit(before, after):
    if MODE == Modes.ANNOY_EVERYONE and \
        TARGET_ID not in [u.id for u in after.mentions]:
        await after.channel.send(
            f"You though you were so clever didn't you {after.author.mention} "
            f">:C\n{random.choice(FEEDBACK_MESSAGES)}")

bot.run(os.getenv('TOKEN'))
