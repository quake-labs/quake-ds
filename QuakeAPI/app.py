from math import degrees, radians, cos, sin, asin, atan2, sqrt
from flask import Flask, jsonify
from .USGSetl import *


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return jsonify({'status_code': 200,
                        'message': 'success, the flask API is running'})

    @app.route('/lastQuake')
    def lastQuake():
        curs = CONN.cursor()
        response = curs.execute('''
            SELECT * FROM USGS
            ORDER BY Time Desc
            limit 1;
        ''')
        quake = curs.fetchone()
        response = {'status_code': 200,
                    'message': {
                        'id': quake[0],
                        'place': quake[1],
                        # time is currently in ms since epoch
                        'time': quake[2],
                        'lat': quake[3],
                        'lon': quake[4],
                        'mag': quake[5],
                        'Oceanic': quake[6]}}
        return jsonify(response)

    @app.route('/last/<time>')
    def getTime(time):
        '''for now this is a super simple function that just uses the USGS API to
        get the last however many quakes. In a future release this will need to
        be improved to read out of our database'''
        if time.upper() not in ['HOUR', 'DAY', 'WEEK', 'MONTH']:
            return jsonify({'status_code': 400,
                            'message': '''please choose from "hour", "day",
                                        "week", or "month"'''})
        else:
            now = get_now()
            message = get_last_quakes(now, time)
            return jsonify({'status_code': 200,
                            'message': message})

    @app.route('/test')
    def testRoute():
        response = query_one('SELECT * FROM USGS where time=1582252014390')
        return jsonify(response)

    @app.route('/history/<float:lat>,<float:lon>,<float:dist>')
    def history(lat, lon, dist):
        '''Calculate the top left and bottom right coordinates at distance dist
        from coordinates lat, lon'''

        lat = radians(lat)
        lon = radians(lon)
        radius = 6371
        top_left = 315
        bottom_right = 135

        lat2A = asin(sin(lat) * cos(dist/radius) +
                     cos(lat) * sin(dist/radius) * cos(top_left))
        lat2B = asin(sin(lat) * cos(dist/radius) +
                     cos(lat) * sin(dist/radius) * cos(bottom_right))

        lon2A = lon + atan2(sin(top_left) * sin(dist/radius) *
                            cos(lat), cos(dist/radius) - sin(lat) * sin(lat2A))
        lon2B = lon + atan2(sin(bottom_right) * sin(dist/radius) *
                            cos(lat), cos(dist/radius) - sin(lat) * sin(lat2B))

        coordinates = {
            "lonA": degrees(lon2A),
            "latA": degrees(lat2A),
            "lonB": degrees(lon2B),
            "latB": degrees(lat2B)
        }

        return jsonify(coordinates)

    return app
