from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import time
from DBQueries import *
from datetime import datetime

CREATE_EMSC = '''CREATE TABLE EMSC
                (ID SERIAL PRIMARY KEY,
                Place text,
                Time bigint,
                Latitude float,
                Longitude float,
                Magnitude float)'''


def setup_EMSC(pages):
    CONN = connect()
    curs = CONN.cursor()
    curs.execute('DROP TABLE IF EXISTS EMSC')
    print('Table Dropped')
    curs.execute(CREATE_EMSC)
    curs.close()
    CONN.commit()
    CONN.close()
    fill_db(pages)


def get_table(i):
    url = 'https://www.emsc-csem.org/Earthquake/?view='+str(i)
    try:
        page = requests.get(url, timeout=5)
    except:
        print(f'request {i} timed out, trying again')
        return get_table(i)
    page_soup = BeautifulSoup(page.text, 'html.parser')
    try:
        table = page_soup.find('tbody')
        rows = table.find_all('tr')
    except:
        print(f'request {i} returned no table, trying again')
        return get_table(i)
    page_insert = 'INSERT INTO EMSC (Place, Time, Latitude, Longitude, Magnitude) VALUES '
    for i, row in enumerate(rows):
        try:
            cells = row.find_all('td')
            rawTime = row.find(class_="tabev6").find('a').text
            timestring = re.sub('\xa0\xa0\xa0', ' ', rawTime)
            dt = datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S.%f')
            time = dt.timestamp() * 1000
            lat = float(cells[4].text) if cells[5].text.strip(
                '\xa0') == 'N' else -float(cells[4].text)
            lon = float(cells[6].text) if cells[7].text.strip(
                '\xa0') == 'E' else -float(cells[6].text)
            mag = float(cells[10].text)
            place = re.sub("'", "''", cells[11].text.strip('\xa0'))
            row_insert = f"('{place}', {time}, {lat}, {lon}, {mag}), "
            page_insert += row_insert
            #print(f'row {i}, {place} added')
        except:
            print('passed row')

    return page_insert[:-2]+';'


def fill_db(pages):
    CONN = connect()
    curs = CONN.cursor()
    for i in range(1, pages+1):
        print(f'starting page {i}')
        query = get_table(i)
        print('starting insertion')
        curs.execute(query)
        print('insertion complete')
        curs.close()
        CONN.commit()
        curs = CONN.cursor()
        print(f'page {i} completed')
    curs.close()
    CONN.commit()
    CONN.close()


if __name__ == '__main__':
    setup_EMSC(20)
