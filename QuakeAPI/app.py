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
            return jsonify({'status_code': 200,
                            'message':
                            get_recent_quakes(os.environ[time.upper()])})

    @app.route('/test')
    def testRoute():
        response = query_one('SELECT * FROM USGS where time=1582252014390')
        return jsonify(response)

    @app.route('/history/<lat>,<lon>,<dist>')
    def history(lat, lon, dist):
        # oof I just googled it and this is gonna be rough
        pass

    return app
