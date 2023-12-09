# imports
import asyncio
import pprint
import time
import urllib
from datetime import datetime
from urllib.request import urlopen

import requests

from ptn.spyplane.bot import bot
from ptn.spyplane.constants import channel_scout, bot_guild

# local constants

"""
Helpers for main functions
"""


def get_faction_systems():
    # Define the API endpoint and the parameters
    api_endpoint = "https://elitebgs.app/api/ebgs/v5/factions"
    params = {'name': 'Pilots Trade Network'}

    # Make a GET request to the API
    response = requests.get(api_endpoint, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        system_info = [faction['faction_presence'] for faction in data['docs']]
        pprint.pp(system_info)
    else:
        print(f"Failed to retrieve data: {response.status_code}")


def fetch_current_tick() -> int:
    hdr = {
        'User-Agent': 'curl/7.68.0',
        'Accept': '*/*'
    }
    link = "https://elitebgs.app/api/ebgs/v5/ticks"
    response = requests.get(link)
    return response.json()


print(fetch_current_tick())


def time_to_timestamp(date_str):
    date_format = "%d/%m/%Y %H:%M:%S"
    datetime_obj = datetime.strptime(date_str, date_format)

    return int(time.mktime(datetime_obj.timetuple()))

async def clear_scout_messages():
    guild = bot.get_guild(bot_guild())
    scout_channel = guild.get_channel(channel_scout())

    # Clear messages
    messages = [message async for message in scout_channel.history(limit=None)]
    non_pinned_messages = [message for message in messages if not message.pinned]
    await scout_channel.delete_messages(non_pinned_messages)
