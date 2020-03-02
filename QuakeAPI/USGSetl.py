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
    recents = get_recent_quakes(HOUR)
    print('got quakes')
    for quake in recents:
        Place = quake['place']
        Time = quake['time']
        Latitude = quake['latitude']
        Longitude = quake['longitude']
        Magnitude = quake['magnitude']
        Oceanic = quake['Oceanic']
        insert_query = f"""INSERT INTO USGS
                        (Place, Time, Latitude, Longitude, Magnitude, Oceanic)
                        VALUES
                        ('{Place}', {Time}, {Latitude}, {Longitude},
                        {Magnitude}, {Oceanic})"""
        print(Place)
        curs.execute(insert_query)
        curs.close()
        CONN.commit()
        curs = CONN.cursor()


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
        quake_data['longitude'] = quake['geometry']['coordinates'][1]
        quake_data['latitude'] = quake['geometry']['coordinates'][0]
        quake_data['place'] = re.sub("[']", "''", quake['properties']['place'])
        quake_data['time'] = quake['properties']['time']
        quake_list.append(quake_data)
    return quake_list


def print_results(results):
    for result in results:
        print(result['time'], result['place'])


def insert_quakes(recents, period):
    '''this function takes in an extracted and transformed list of recent
    earthquakes and inserts them into the database, checking to make sure that
    the quake isn't already there. Once it finds a duplicate it stops inserting
    '''
    print('insertion called')
    curs = CONN.cursor()
    print('cursor created')
    last_time = get_last_times(recents[0]['time'], period)
    print('last quakes aquired')
    for quake in recents:
        if quake['time'] in last_time:
            print('old:', quake['place'], quake['Oceanic'])
        else:
            Place = quake['place']
            Time = quake['time']
            Latitude = quake['latitude']
            Longitude = quake['longitude']
            Magnitude = quake['magnitude']
            Oceanic = quake['Oceanic']
            insert_query = f"""INSERT INTO USGS
                        (Place, Time, Latitude, Longitude, Magnitude, Oceanic)
                        VALUES ('{Place}', {Time}, {Latitude}, {Longitude},
                        {Magnitude}, {Oceanic})"""
            curs.execute(insert_query)
            curs.close()
            CONN.commit()
            curs = CONN.cursor()
            print(f"new: {quake['place']}, {quake['Oceanic']} inserted")


def get_last_times(now, period='hour'):
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

    for t in time:
        times.append(t[0])

    return times


def pipe_data(url):
    '''this function takes in a url, gets the recent earthquakes,
    then loads the new quakes into the database'''
    recents = get_recent_quakes(url)
    insert_quakes(recents, 'hour')


def get_last_quakes(now, period='hour'):
    curs = CONN.cursor()
    quake_list = []
    if period.upper() == 'HOUR' or period == HOUR:
        print('collecting one HOUR')
        curs.execute(f'SELECT * FROM USGS WHERE time >= {now-3.6e6}')
        quakes = curs.fetchall()
    elif period.upper() == 'DAY' or period == DAY:
        curs.execute(f'SELECT * FROM USGS WHERE time >= {now-8.64e7}')
        quakes = curs.fetchall()
    elif period.upper() == 'WEEK' or period == WEEK:
        curs.execute(f'SELECT * FROM USGS WHERE time >= {now-6.048e+8}')
        quakes = curs.fetchall()
    elif period.upper() == 'MONTH' or period == MONTH:
        curs.execute(f'SELECT * FROM USGS WHERE time >= {now-2.628e+9}')
        quakes = curs.fetchall()
    else:
        quakes = []

    for quake in quakes:
        quake_list.append({'id': quake[0],
                           'place': quake[1],
                           # time is currently in ms since epoch
                           'time': quake[2],
                           'lat': quake[3],
                           'lon': quake[4],
                           'mag': quake[5],
                           'Oceanic': quake[6]})

    return quake_list


def get_now():
    curs = CONN.cursor()
    curs.execute('SELECT time FROM USGS ORDER BY time desc limit 1;')
    time = curs.fetchall()
    return time[0][0]


if __name__ == '__main__':
    setup_USGS()
