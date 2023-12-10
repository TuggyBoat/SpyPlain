import datetime

import socketio

from ptn.spyplane.database.database import get_last_tick, insert_tick
from ptn.spyplane.modules.SystemScouter import delayed_scout_update

# socket
sio = socketio.AsyncClient()


@sio.event
async def connect():
    print('Successful connection established with tick detector')


@sio.event
async def disconnect():
    print('Disconnected from tick detector')


# Tick message detection
@sio.event
async def message(data):
    print('Tick received:', data)
    await check_tick(data)


async def start_client():
    await sio.connect('https://tick.edcd.io/')
    await sio.wait()


def to_datetime(datetime_string: str):
    dt_object = datetime.datetime.fromisoformat(datetime_string)
    dt_obj_utc = dt_object.astimezone(datetime.timezone.utc)
    return dt_obj_utc.timestamp()


async def check_tick(data: str):
    # convert tick to time.time() timestamp
    timestamp = int(to_datetime(data))

    # get last tick
    last_tick = await get_last_tick()
    try:
        last_tick = last_tick[0].tick_time
    except:
        last_tick = False

    # if this is the first tick
    if not last_tick:
        print('Populating tick table with first tick')
        await insert_tick(timestamp)
        await delayed_scout_update()

    # if the tick is the same (happens when restarting/reconnecting)
    elif last_tick == timestamp:
        print('Ticks are equal, skipping...')
        return

    elif last_tick < timestamp:
        if not last_tick:
            print('New tick detected')
            await insert_tick(timestamp)
