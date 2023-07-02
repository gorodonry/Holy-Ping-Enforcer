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


# Associated constants for yes/no question function.
VALID_ANSWERS = ("y", "yes", "n", "no")
POSITIVE_ANSWERS = ("y", "yes")

# Server information.
USER_IDS = {"Ryan": 877750921474502717, "Sofia": 424719746869624865}
CHANNEL_IDS = {
    "General": 1084971815996227765,
    "Suggestions": 1083873072785936495,
    "Announcements": 1083867162046890055,
    "Testing": 1113427709616463922
}

# Define global variables.
target_id = None
mode = None

# Other also important constants.
FEEDBACK_MESSAGES = [
    f"You've been naughty :index_pointing_at_the_viewer: - grabbing "
    f"<@{target_id}> rn",
    "404 Ping Not Found", f"Smhhh, no ping for <@{target_id}> :(((",
    f"Shouldn't say such things without <@{target_id}> :pensive:",
    "Nuh uh, that's not the kind of language we use in here",
    f"Check the new admin policy re <@{target_id}>",
    "<:angery:1092655340727849041>"
]

PRIDE_MESSAGES = [
    "<:redguy:1106525937136324688> <:orangeguy:1106525377708429352> "
    "<:yellowguy:1106524765977583657> <:greenguy:1095161810870607953> "
    "<:blueguy:1095161113773101229> <:pinkguy:1106523189238050886> "
    "<:purpleguy:1106524177663528990>"
]

MIN_TIME = 60 * 60 * 3  # 3 hours (seconds)
MAX_TIME = 60 * 60 * 30  # 30 hours (seconds)

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


def ask_yes_no_question(prompt):
    """Asks a yes or no question and returns the answer as True or False."""
    answer = ""
    while answer not in VALID_ANSWERS:
        answer = input(prompt).strip().lower()
        if answer not in VALID_ANSWERS:
            print("Please enter either yes or no.")
    return answer in POSITIVE_ANSWERS


def determine_target() -> str:
    """Asks for a target and returns the user ID."""
    print(f"Known entities: {', '.join(USER_IDS.keys)}")

    valid_target = False
    while not valid_target:
        target = input("Pick a target: ").strip().lower().capitalize()
        if target in USER_IDS.keys:
            valid_target = True
        else:
            print("Invalid target.")

    return USER_IDS[target]


@bot.event
async def on_ready():
    global sleep_time, mode, target_id

    # Determine mode and target.
    print("""Annoy everyone ---> 0
Reminder ---> 1
Random pings ---> 2
Pride month ---> 3""")

    mode_resolved = False
    while not mode_resolved:
        try:
            mode = int(input("Enter your choice: ").strip())
            if mode >= 0 and mode <= 3:
                mode_resolved = True
        except ValueError:
            print("Don't be ridiculous.")

    match mode:
        case 0:
            mode, target_id = Modes.ANNOY_EVERYONE, determine_target()
        case 1:
            mode, target_id = Modes.REMINDER, determine_target()
        case 2:
            mode, target_id = Modes.RANDOM_PINGS, determine_target()
        case 3:
            mode = Modes.PRIDE_MONTH
            pride_month_starting = ask_yes_no_question(
                "Is pride month starting? ")
        case _:
            raise ValueError("Mode undefined")

    print(f'Bot is ready. Logged in as {bot.user.name}')

    await bot.get_channel(CHANNEL_IDS["Testing"]).send("The bot has started")

    if mode not in (Modes.REMINDER, Modes.PRIDE_MONTH):
        return

    if mode == Modes.PRIDE_MONTH and pride_month_starting:
        await bot.get_channel(CHANNEL_IDS["Testing"]).send(
            f"{PRIDE_MESSAGES[0]} Pride month is here :D "
            f"{' '.join(list(reversed(PRIDE_MESSAGES[0].split())))}")

    if mode == Modes.PRIDE_MONTH:
        await bot.change_presence(
            activity=discord.Game(name="happy pride month!"))

    while True:
        sleep_time = random.randint(MIN_TIME, MAX_TIME)
        await asyncio.sleep(sleep_time)
        match mode:
            case Modes.REMINDER:
                if recent_channel is not None:
                    await recent_channel.send(
                        f"<@{target_id}> Here's your random reminder :)")
            case Modes.PRIDE_MONTH:
                await bot.get_channel(CHANNEL_IDS["Testing"]).send(
                    random.choice(PRIDE_MESSAGES))
            case _:
                pass


@bot.event
async def on_message(message):
    global recent_channel

    match mode:
        case Modes.ANNOY_EVERYONE:
            if target_id not in [u.id for u in message.mentions]:
                await message.channel.send(
                    f"{message.author.mention} "
                    f"{random.choice(FEEDBACK_MESSAGES)}")
        case Modes.REMINDER:
            recent_channel = message.channel
        case Modes.RANDOM_PINGS:
            if random.randint(1, 100) > 98:
                if target_id not in [u.id for u in message.mentions]:
                    await message.channel.send(
                        f"{message.author.mention} "
                        f"{random.choice(FEEDBACK_MESSAGES)}")
        case _:
            pass

    await bot.process_commands(message)


@bot.event
async def on_message_edit(before, after):
    if mode == Modes.ANNOY_EVERYONE and \
        target_id not in [u.id for u in after.mentions]:
        await after.channel.send(
            f"You though you were so clever didn't you {after.author.mention} "
            f">:C\n{random.choice(FEEDBACK_MESSAGES)}")

bot.run(os.getenv('TOKEN'))
