from .DBQueries import *
import re

'''this file will contain all the general functions the API needs to mess with
quakes. It is being pulled from USGSetl and EMSCscrape'''


def print_results(results):
    '''This is a helper function that makes it a little more human readable'''
    for result in results:
        print(result['time'], result['place'])


def get_last_quakes(now, source, period='hour', mag=5.5):
    '''This function gets the last quakese over a given period and magnitude.
    Now is time in unix time (MS), generally comes from the last quake in the
    DB
    Source is 'USGS' or 'EMSC'
    Period is 'HOUR', 'DAY', 'WEEK', or 'MONTH'
    Mag is a float with default value 5.5'''
    CONN = connect()
    curs = CONN.cursor()
    quake_list = []
    if period.upper() == 'HOUR' or period == HOUR:
        curs.execute(f'''SELECT * FROM {source} WHERE time >= {now-3.6e6}
                     and Magnitude >= {mag}''')
        quakes = curs.fetchall()
    elif period.upper() == 'DAY' or period == DAY:
        curs.execute(f'''SELECT * FROM {source} WHERE time >= {now-8.64e7}
                     and Magnitude >= {mag}''')
        quakes = curs.fetchall()
    elif period.upper() == 'WEEK' or period == WEEK:
        curs.execute(f'''SELECT * FROM {source} WHERE time >= {now-6.048e+8}
                     and Magnitude >= {mag}''')
        quakes = curs.fetchall()
    elif period.upper() == 'MONTH' or period == MONTH:
        curs.execute(f'''SELECT * FROM {source} WHERE time >= {now-2.628e+9}
                     and Magnitude >= {mag}''')
        quakes = curs.fetchall()
    else:
        quakes = []

    curs.close()
    CONN.commit()
    CONN.close()

    for quake in quakes:
        quake_list.append({'id': quake[0],
                           'place': quake[1],
                           # time is currently in ms since epoch
                           'time': quake[2],
                           'lat': quake[3],
                           'lon': quake[4],
                           'mag': quake[5],
                           'Oceanic': quake[6] if source == 'USGS' else None})

    return quake_list


def get_now():
    '''a funciton to get the time of the last quake to get an approximate
    estimation of the current time. This method was selected for simplicity.'''

    CONN = connect()
    curs = CONN.cursor()
    curs.execute('SELECT time FROM USGS ORDER BY time desc limit 1;')
    time = curs.fetchall()
    curs.close()
    CONN.commit()
    CONN.close()
    return time[0][0]
