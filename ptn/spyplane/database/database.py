"""
Functions relating to databases used by spyplane.

Depends on: constants

Error handling: errors originating from Discord commands should be handled in their respective Cogs and outputted to user
                errors occuring on startup functions should be handled within those functions and outputted to terminal
"""

# libraries
import asyncio
import enum
import sqlite3
import os

# local classes
from ptn.spyplane.classes.ConfigData import ConfigData

# local constants
import ptn.spyplane.constants as constants
from ptn.spyplane.classes.TickData import TickData

"""
STARTUP FUNCTIONS
"""


# ensure all paths function for a clean install
def build_directory_tree_on_startup():
    print("Building directory tree...")
    try:
        os.makedirs(constants.DB_PATH, exist_ok=True)  # /database - the main database files
        os.makedirs(constants.SQL_PATH, exist_ok=True)  # /database/db_sql - DB SQL dumps
        os.makedirs(constants.BACKUP_DB_PATH, exist_ok=True)  # /database/backups - db backups
    except Exception as e:
        print(f"Error building directory tree: {e}")


build_directory_tree_on_startup()  # build directory structure


# build or modify database as needed on startup
def build_database_on_startup():
    print("Building database...")
    try:
        database_table_map = {
            'config_data': {'obj': spyplane_db, 'create': config_table_create},
            'tick_times': {'obj': spyplane_db, 'create': tick_times_table_create},
            'scout_data': {'obj': spyplane_db, 'create': scout_data_table_create}
        }

        for table_name in database_table_map:
            t = database_table_map[table_name]
            if not check_database_table_exists(table_name, t['obj']):
                create_missing_table(table_name, t['obj'], t['create'])
            else:
                print(f'{table_name} table exists, do nothing')
    except Exception as e:
        print(f"Error building database: {e}")


# defining infraction table for database creation
config_table_create = '''
    CREATE TABLE config_data(
        config_setting TEXT NOT NULL,
        config_value TEXT NOT NULL
    )
    '''
tick_times_table_create = '''
    CREATE TABLE tick_times(
        entry_id INTEGER PRIMARY KEY,
        tick_time INTEGER NOT NULL
    )
'''
scout_data_table_create = '''
    CREATE TABLE scout_data(
        entry_id INTEGER PRIMARY KEY,
        system_name TEXT NOT NULL,
        username TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        timestamp INTEGER NOT NULL
    )
'''


# function to check if a given table exists in a given database
def check_database_table_exists(table_name, database):
    """
    Checks whether a table exists in the database already.

    :param str table_name:  The database string name to create.
    :param sqlite.Connection.cursor database: The database to connect againt.
    :returns: A boolean state, True if it exists, else False
    :rtype: bool
    """
    print(f'Starting up - checking if {table_name} table exists or not')

    database.execute(f"SELECT count(name) FROM sqlite_master WHERE TYPE = 'table' AND name = '{table_name}'")
    return bool(database.fetchone()[0])


# function to create a missing table / database
def create_missing_table(table, db_obj, create_stmt):
    """
    :param table:
    :param db_obj:
    :param create_stmt:
    """
    print(f'{table} table missing - creating it now')

    if os.path.exists(os.path.join(os.getcwd(), 'db_sql', f'{table}_dump.sql')):

        # recreate from backup file
        print('Recreating database from backup ...')
        with open(os.path.join(os.getcwd(), 'db_sql', f'{table}_dump.sql')) as f:

            sql_script = f.read()
            db_obj.executescript(sql_script)

    else:
        # Create a new version
        print('No backup found - Creating empty database')

        db_obj.execute(create_stmt)


"""
DATABASE OBJECT

Database connection, cursor, and lock
"""

# connect to infraction database
spyplane_conn = sqlite3.connect(constants.INFRACTIONS_DB_PATH)
spyplane_conn.row_factory = sqlite3.Row
spyplane_db = spyplane_conn.cursor()

# lock infraction db
spyplane_db_lock = asyncio.Lock()


async def insert_scout_log(system_name, username, user_id, timestamp):
    """
    Inserts a new scout_log into the database

    :param system_name:
    :param username:
    :param user_id:
    :param timestamp:
    :return: int
    """

    print(f'Inserting scout log for {username}.')

    try:
        await spyplane_db_lock.acquire()

        spyplane_db.execute(
            f"INSERT INTO scout_data (system_name, username, user_id, timestamp) VALUES (?, ?, ?, ?)",
            (system_name, username, user_id, timestamp)
        )
        spyplane_conn.commit()

        entry_id = spyplane_db.lastrowid

    finally:
        spyplane_db_lock.release()

    print(f"Scout log inserted with entry ID {entry_id}.")

    return entry_id


async def insert_tick(tick_time: int):
    try:
        await spyplane_db_lock.acquire()

        spyplane_db.execute(
            f"INSERT INTO tick_times (tick_time) VALUES ({tick_time})",
        )
        spyplane_conn.commit()

        entry_id = spyplane_db.lastrowid

    finally:
        spyplane_db_lock.release()

    print(f"Scout log inserted with entry ID {entry_id}.")

    return entry_id


async def get_last_tick():
    """
    Get the last inserted tick from database

    :return: dict
    """
    query = "SELECT * FROM tick_times ORDER BY entry_id DESC LIMIT 1"
    spyplane_db.execute(query)

    tick_data = [TickData(tick) for tick in spyplane_db.fetchall()]

    return tick_data
