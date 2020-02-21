import requests
import re
from .DBQueries import *
from datetime import datetime
import pytz

HOUR = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson'
DAY = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson'
WEEK = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson'
MONTH = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson'

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
    '''This function gets all the quakes from USGS
    it takes in a url as an argument, which can be any of the gloabl variables in this
    package'''
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


if __name__ == '__main__':
    setup_USGS()
