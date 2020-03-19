from flask import Flask, jsonify
from .history import history as hist
from .USGSetl import *


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return jsonify({'status_code': 200,
                        'message': 'success, the flask API is running'})

    @app.route('/lastQuake')
    @app.route('/lastQuake/<mag>')
    def lastQuake(mag=5.5):
        # sanitize inputs
        try:
            try:
                magn = float(mag)
            except:
                magn = int(mag)
            if float(mag) < 0 or float(mag) > 11:
                print(mag)
                raise Exception
        except:
            print('this route caused an error')
            return jsonify({'status_code': 400, 'message':
                            'please enter a magnitude between 0 and 11'})
        curs = CONN.cursor()
        response = curs.execute(f'''
            SELECT * FROM USGS
            WHERE Magnitude >= {mag}
            ORDER BY Time Desc
            limit 1;
        ''')
        quake = curs.fetchone()
        response = {
            'id': quake[0],
            'place': quake[1],
            # time is currently in ms since epoch
            'time': quake[2],
            'lat': quake[3],
            'lon': quake[4],
            'mag': quake[5],
            'Oceanic': quake[6]
        } if quake is not None else f'No quakes of magnitude {mag} or higher'

        return jsonify({'status_code': 200, 'message': response})

    @app.route('/last/<time>/<mag>')
    @app.route('/last/<time>')
    def getTime(time, mag=5.5):
        '''for now this is a super simple function that just uses the USGS API to
        get the last however many quakes. In a future release this will need to
        be improved to read out of our database'''
        # sanitize inputs
        try:
            try:
                magn = float(mag)
            except:
                magn = int(mag)
            if float(mag) < 0 or float(mag) > 11:
                print(mag)
                raise Exception
        except:
            print('this route caused an error')
            return jsonify({'status_code': 400, 'message':
                            'please enter a magnitude between 0 and 11'})

        if time.upper() not in ['HOUR', 'DAY', 'WEEK', 'MONTH']:
            return jsonify({'status_code': 400,
                            'message': '''please choose from "hour", "day",
                                        "week", or "month"'''})
        else:
            now = get_now()
            message = get_last_quakes(now, time, mag)
            return jsonify({'status_code': 200,
                            'message': message})

    @app.route('/test')
    def testRoute():
        response = query_one('SELECT * FROM USGS where time=1582252014390')
        return jsonify(response)

    @app.route('/history/<lat>,<lon>,<dist>')
    def history(lat, lon, dist):
        '''Start at coordinates (lat, lon) find the diagonal coordinates
        with distance (dist) and find earthquakes within that square range'''
        lat = float(lat)
        lon = float(lon)
        dist = float(dist)
        coordinates = hist(lat, lon, dist)
        lonA = coordinates['lonA']
        latA = coordinates['latA']
        lonB = coordinates['lonB']
        latB = coordinates['latB']

        if latA < lat:
            latA = 90.0
        if latB > lat:
            latB = -90.0

        longitude_check = f'(Longitude BETWEEN {lonA} AND {lonB})'
        if lonA < -180:
            lonA = lonA + 360
            longitude_check = f'(Longitude > {lonA} AND Longitude < {lonB})'
        if lonB > 180:
            lonB = lonB - 360
            longitude_check = f'(Longitude > {lonA} AND Longitude < {lonB})'

        history_query = f'''
        SELECT * FROM USGS
        WHERE (Latitude BETWEEN {latB} AND {latA})
        AND {longitude_check};
        '''

        curs = CONN.cursor()
        curs.execute(history_query)
        history = curs.fetchall()
        
        return jsonify({'status_code': 200, 'message': history})

    return app
