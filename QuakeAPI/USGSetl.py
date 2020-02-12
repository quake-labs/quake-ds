import requests
import pandas as pd
import re
from DBQueries import *

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
    curs = CONN.cursor()
    try:
        curs.execute('DROP TABLE USGS;')
    except Exception as error:
        curs.close()
        CONN.commit()
        curs = CONN.cursor()
    curs.execute(CREATE_USGS_QUERY)
    recents = get_recent_quakes(HOUR)
    for quake in recents:
        Place = quake['place']
        Time = quake['time']
        Latitude = quake['latitude']
        Longitude = quake['longitude']
        Magnitude = quake['magnitude']
        Oceanic = bool(quake['tsunami'])
        insert_query = f"INSERT INTO USGS (Place, Time, Latitude, Longitude, Magnitude, Oceanic) VALUES ('{Place}', {Time}, {Latitude}, {Longitude}, {Magnitude}, {Oceanic})"
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
        quake_data['ids'] = quake['properties']['ids'].split(',')
        quake_data['id'] = quake['id']

        quake_data['place'] = re.sub("[']", "''", quake['properties']['place'])

        quake_data['time'] = quake['properties']['time']
        quake_data['latitude'] = quake['geometry']['coordinates'][0]
        quake_data['longitude'] = quake['geometry']['coordinates'][1]
        quake_data['magnitude'] = quake['properties']['mag']
        quake_data['tsunami'] = quake['properties']['tsunami']
        quake_list.append(quake_data)
    return quake_list

def insert_quakes(recents):
    curs = CONN.cursor()
    last_time = curs.execute('SELECT TIME FROM USGS ORDER BY time DESC LIMIT 1;').fetchone()[0]
    for quake in recents:
        if quake['time'] == last_time:
            print(quake['place'])
            return None
        else:
            Place = quake['place']
            Time = quake['time']
            Latitude = quake['latitude']
            Longitude = quake['longitude']
            Magnitude = quake['magnitude']
            Oceanic = quake['tsunami']
            insert_query = f"INSERT INTO USGS (Place, Time, Latitude, Longitude, Magnitude, Oceanic) VALUES ('{Place}', {Time}, {Latitude}, {Longitude}, {Magnitude}, {Oceanic})"
            curs.execute(insert_query)
            curs.close()
            CONN.commit()
            curs = CONN.cursor()

def pipe_data(url):
    '''this function takes in a url, gets the recent earthquakes,
    then loads the new quakes into the database'''
    recents = get_recent_quakes(url)
    insert_quakes(recents)

if __name__=='__main__':
    setup_USGS()
