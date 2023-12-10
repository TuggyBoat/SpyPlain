import asyncio
import pprint

import discord
import requests

from ptn.spyplane.bot import bot
from ptn.spyplane.constants import bot_guild, channel_scout
from ptn.spyplane.database.database import get_system_state_interval, get_monitoring_channel_id
from ptn.spyplane.modules.Sheets import get_systems


async def get_faction_states_in_system(systemName: str):
    api_endpoint = "https://www.edsm.net/api-system-v1/factions"
    params = {'systemName': systemName}
    response = requests.get(api_endpoint, params=params)
    expansion_factions = set()
    other_states_system_info = {}
    if response.status_code == 200:
        data = response.json()
        for faction in data['factions']:
            if any(state['state'] == 'Expansion' for state in faction['activeStates'] + faction['pendingStates']):
                expansion_factions.add(faction['name'])
            elif any(state['state'] != 'Expansion' for state in faction['activeStates'] + faction['pendingStates']):
                other_states_system_info[faction['name']] = {'activeStates': faction['activeStates'],
                                                             'pendingStates': faction['pendingStates']}

    else:
        print(f"Failed to retrieve data for {systemName}: {response.status_code}")

    return expansion_factions, other_states_system_info


async def get_faction_states_in_scout_systems(scoutList: list):
    """
    Gets a system's factions and their states, splitting
    :param scoutList: list
    :return: set, dict
    """
    all_expansion_factions = set()
    all_other_states_systems_info = {}

    print('Call for system states, gathering...')

    for system in scoutList:
        expansion_factions, other_states_system_info = await get_faction_states_in_system(system[0])
        all_expansion_factions.update(expansion_factions)
        if other_states_system_info:
            all_other_states_systems_info[system[0]] = other_states_system_info

    print('Gathered systems states, returning...')

    return all_expansion_factions, all_other_states_systems_info


async def create_faction_states_embed():
    expanding_factions, other_states_factions = await get_faction_states_in_scout_systems(get_systems())
    body = '**Expanding Factions**'
    for expanding_faction in expanding_factions:
        body += '\n' + expanding_faction

    body += '\n\n**Other States in Systems**'
    for system, factions in other_states_factions.items():
        body += f'\n**{system}**:'
        for faction_name, states in factions.items():
            active_states = ', '.join([state['state'] for state in states['activeStates']])
            pending_states = ', '.join([state['state'] for state in states['pendingStates']])

            if active_states:
                body += f'\n- {faction_name} - Active: {active_states}'
            if pending_states:
                body += f'\n- {faction_name} - Pending: {pending_states}'
    print('Generated embed for faction states')
    embed = discord.Embed(title='Faction States in PTN Space', description=body)
    return embed


async def post_system_state_report():
    guild = bot.get_guild(bot_guild())
    monitoring_channel = guild.get_channel(await get_monitoring_channel_id())
    embed = await create_faction_states_embed()
    await monitoring_channel.send(embed=embed)


async def delayed_system_state_update():
    """
    Runs the system states report after a set amount of time
    """
    system_state_interval = await get_system_state_interval()
    print('System State Reporting interval is '+str(system_state_interval))
    # clear channel
    await asyncio.sleep(system_state_interval)  # sleep an amount of time
    await post_system_state_report()
