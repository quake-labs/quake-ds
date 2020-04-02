import json
import psycopg2
from bs4 import BeautifulSoup
import requests
from config import *
import re
from datetime import datetime


CONN = psycopg2.connect(user=toyUSER,
                        password=toyPASSWORD,
                        host=toyHOST,
                        dbname=toyNAME,
                        port=5432)


def query(query):
    curs = CONN.cursor()
    try:
        curs.execute(query)
    except:
        print('Query error')
    curs.close()
    CONN.commit()


class EMSC_scraper():
    '''turning the functions above which pass around random data into a single
    class so that it can work as an object'''

    def __init__(self):
        # the page and row number to start collecting from
        self.page_num = 0  # first thing that happens is to incriment this
        self.row_num = 0
        # set the url that everything else will reference
        self.url = 'https://www.emsc-csem.org/Earthquake/?view='

    def find_yesterday(self):
        '''basic function to advance the object to start at yesterday.
           Needs to be run before get_yesterday'''
        today = True
        while(today):
            self.page_num += 1
            page = requests.get(self.url+str(self.page_num), timeout=5)
            page_soup = BeautifulSoup(page.text, 'html.parser')
            table = page_soup.find('tbody')
            rows = table.find_all('tr')
            for num, row in enumerate(rows):
                if row['class'][0] == 'autour':
                    today = False
                    self.row_num = num + 3  # get over the day break
                    break

    def get_yesterday(self):
        '''gets the quakes and saves them to a list'''
        yesterday = True
        self.quakes = []
        while(yesterday):
            page = requests.get(self.url+str(self.page_num), timeout=5)
            page_soup = BeautifulSoup(page.text, 'html.parser')
            table = page_soup.find('tbody')
            rows = table.find_all('tr')
            for row in rows[self.row_num:]:
                if row['class'][0] != 'autour':
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
                    self.quakes.append({'time': time,
                                        'lat': lat,
                                        'lon': lon,
                                        'mag': mag,
                                        'place': place})
                else:
                    yesterday = False
                    break
            self.page_num += 1
            self.row_num = 0

    def construct_query(self):
        self.day_insert = 'INSERT INTO EMSC (place, time, lat, lon, mag) VALUES '
        for quake in self.quakes:
            row_insert = f"('{quake['place']}', '{quake['time']}', {quake['lat']}, {quake['lon']}, {quake['mag']}), "
            self.day_insert += row_insert
        self.day_insert = self.day_insert[:-2]+';'

    def query_yesterday(self):
        self.find_yesterday()
        self.get_yesterday()
        self.construct_query()
        return self.day_insert


def lambda_handler(event, context):
    scraper = EMSC_scraper()
    query(scraper.query_yesterday())
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


if __name__ == '__main__':
    scrapper = EMSC_scraper()
    scrapper.find_yesterday()
    scrapper.get_yesterday()
    print(scrapper.quakes)
