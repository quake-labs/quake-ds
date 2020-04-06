from flask import Flask, jsonify
from .history import history as hist
from .api_funcs import *


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return jsonify({'status_code': 200,
                        'message': 'success, the flask API is running'})

    @app.route('/lastQuake/<source>')
    @app.route('/lastQuake/<source>/<float:mag>')
    def lastQuake(source, mag=5.5):
        CONN = connect()
        # sanitize inputs
        if mag < 0 or mag > 11:
            return jsonify({'status_code': 400, 'message':
                            'please enter a magnitude between 0 and 11'})
        # check to make sure that source is valid
        if source.upper() not in ['USGS', 'EMSC']:
            return jsonify({'status_code': 400,
                            'message': 'Please select either USGS or EMSC as source'})
        curs = CONN.cursor()
        response = curs.execute(f'''
            SELECT * FROM {source}
            WHERE Magnitude >= {mag}
            ORDER BY Time Desc
            limit 1;
        ''')
        quake = curs.fetchone()
        curs.close()
        CONN.commit()
        CONN.close()
        response = prep_response(quake, source) if quake is not None \
            else f'No quakes of magnitude {mag} or higher in {source}'
        return jsonify({'status_code': 200, 'message': response})

    @app.route('/last/<source>/<time>/<mag>')
    @app.route('/last/<source>/<time>')
    def getTime(time, source, mag=5.5):
        '''This route pulls the last quakes from USGS over the specified time
        frame that are at or above the specified magnitude.
        Source is 'USGS' or 'EMSC'
        Mag is a float with default 5.5
        Options for time are 'HOUR', 'DAY', 'WEEK', or 'MONTH' '''
        # sanitize inputs
        try:
            sanitize_mag(mag)
        except:
            print('this route caused an error')
            return jsonify({'status_code': 400, 'message':
                            'please enter a magnitude between 0 and 11'})

        # verify that time is a valid input
        if time.upper() not in ['HOUR', 'DAY', 'WEEK', 'MONTH']:
            return jsonify({'status_code': 400,
                            'message': '''please choose from "hour", "day",
                                        "week", or "month"'''})
        if source.upper() not in ['USGS', 'EMSC']:
            return jsonify({'status_code': 400,
                            'message': 'Please select either USGS or EMSC as source'})
        now = get_now()
        message = get_last_quakes(now, source, time, mag)
        return jsonify({'status_code': 200,
                        'message': message})

    @app.route('/test')
    def testRoute():
        response = query_one('SELECT * FROM USGS where time=1582252014390')
        return jsonify(response)

    @app.route('/history/<float:lat>,<float:lon>,<float:dist>')
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
