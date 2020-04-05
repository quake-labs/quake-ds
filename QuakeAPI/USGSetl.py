import requests
import re
from .DBQueries import *


SOURCE = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/'
HOUR = SOURCE + 'all_hour.geojson'
DAY = SOURCE + 'all_day.geojson'
WEEK = SOURCE + 'all_week.geojson'
MONTH = SOURCE + 'all_month.geojson'

CREATE_USGS_QUERY = '''CREATE TABLE USGS (ID SERIAL PRIMARY KEY,
    Place text,
    Time bigint,
    Latitude float,
    Longitude float,
    Magnitude float,
    Oceanic bool
    )'''


def setup_USGS():
    '''this function is used to set up the initial database, it first drops the
    table if it exists and then creates a new one and fills it with the last
    month of data from USGS.'''
    CONN = connect()
    curs = CONN.cursor()
    print('cusor created ')
    try:
        curs.execute('DROP TABLE USGS;')
        print('table dropped')
    except Exception as error:
        curs.close()
        CONN.commit()
        curs = CONN.cursor()
    curs.execute(CREATE_USGS_QUERY)
    print('table created')
    recents = get_recent_quakes(MONTH)
    print('got quakes')
    for i, quake in enumerate(recents):
        Place = quake['place'] if quake['place'] != None else 'NULL'
        Time = quake['time'] if quake['time'] != None else 'NULL'
        Latitude = quake['latitude'] if quake['latitude'] != None else 'NULL'
        Longitude = quake['longitude'] if quake['longitude'] != None else 'NULL'
        Magnitude = quake['magnitude'] if quake['magnitude'] != None else 'NULL'
        Oceanic = quake['Oceanic'] if quake['Oceanic'] != None else 'NULL'
        insert_query = f"""INSERT INTO USGS
                        (Place, Time, Latitude, Longitude, Magnitude, Oceanic)
                        VALUES
                        ('{Place}', {Time}, {Latitude}, {Longitude},
                        {Magnitude}, {Oceanic})"""
        print(f'{i}/{len(recents)}', Place)
        curs.execute(insert_query)
        curs.close()
        CONN.commit()
        curs = CONN.cursor()
    curs.close()
    CONN.commit()
    CONN.close()


def get_recent_quakes(url):
    '''
    This function gets all the quakes from USGS
    it takes in a url as an argument,
    which can be any of the gloabl variables in this package
    '''
    quakes = requests.get(url)
    quake_list = []
    for quake in quakes.json()['features']:
        quake_data = {}

        quake_data['Oceanic'] = bool(quake['properties']['tsunami'])
        quake_data['magnitude'] = quake['properties']['mag']
        quake_data['longitude'] = quake['geometry']['coordinates'][0]
        quake_data['latitude'] = quake['geometry']['coordinates'][1]
        quake_data['place'] = re.sub("[']", "''", quake['properties']['place'])
        quake_data['time'] = quake['properties']['time']
        quake_list.append(quake_data)
    return quake_list


def insert_quakes(recents, period):
    '''this function takes in an extracted and transformed list of recent
    earthquakes and inserts them into the database, checking to make sure that
    the quake isn't already there.
    It checks for duplicate quakes using the timestamp and only enters unique
    quakes
    '''
    CONN = connect()
    print('insertion called')
    curs = CONN.cursor()
    print('cursor created')
    last_time = get_last_times(recents[0]['time'], period)
    print('last quakes aquired')
    for quake in recents:
        if quake['time'] in last_time:
            print('old:', quake['place'], quake['Oceanic'])
        else:
            Place = quake['place'] if quake['place'] != None else 'NULL'
            Time = quake['time'] if quake['time'] != None else 'NULL'
            Latitude = quake['latitude'] if quake['latitude'] != None else 'NULL'
            Longitude = quake['longitude'] if quake['longitude'] != None else 'NULL'
            Magnitude = quake['magnitude'] if quake['magnitude'] != None else 'NULL'
            Oceanic = quake['Oceanic'] if quake['Oceanic'] != None else 'NULL'
            insert_query = f"""INSERT INTO USGS
                        (Place, Time, Latitude, Longitude, Magnitude, Oceanic)
                        VALUES ('{Place}', {Time}, {Latitude}, {Longitude},
                        {Magnitude}, {Oceanic})"""
            curs.execute(insert_query)
            curs.close()
            CONN.commit()
            curs = CONN.cursor()
            print(f"new: {quake['place']}, {quake['Oceanic']} inserted")
    curs.close()
    CONN.commit()
    CONN.close()


def get_last_times(now, period='hour'):
    CONN = connect()
    curs = CONN.cursor()
    times = []
    if period.upper() == 'HOUR' or period == HOUR:
        print('collecting one HOUR')
        curs.execute(f'SELECT time FROM USGS WHERE time >= {now-3.6e6}')
        time = curs.fetchall()
    elif period.upper() == 'DAY' or period == DAY:
        curs.execute(f'SELECT time FROM USGS WHERE time >= {now-8.64e7}')
        time = curs.fetchall()
    elif period.upper() == 'WEEK' or period == WEEK:
        curs.execute(f'SELECT time FROM USGS WHERE time >= {now-6.048e+8}')
        time = curs.fetchall()
    elif period.upper() == 'MONTH' or period == MONTH:
        curs.execute(f'SELECT time FROM USGS WHERE time >= {now-2.628e+9}')
        time = curs.fetchall()
    else:
        time = []
    curs.close()
    CONN.commit()
    CONN.close()
    for t in time:
        times.append(t[0])

    return times


def pipe_data(url):
    '''this function takes in a url, gets the recent earthquakes,
    then loads the new quakes into the database'''
    recents = get_recent_quakes(url)
    insert_quakes(recents, 'hour')
