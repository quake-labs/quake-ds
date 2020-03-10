from flask import Flask, jsonify
from .USGSetl import *


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return jsonify({'status_code': 200,
                        'message': 'success, the flask API is running'})

    @app.route('/lastQuake', defaults={'mag':5.5})
    @app.route('/lastQuake/<mag>')
    def lastQuake(mag):
        #sanitize inputs
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
        response = {'id': quake[0],
                    'place': quake[1],
                    # time is currently in ms since epoch
                    'time': quake[2],
                    'lat': quake[3],
                    'lon': quake[4],
                    'mag': quake[5],
                    'Oceanic': quake[6]} if quake!=None else f'No quakes of magnitude {mag} or higher'
        return jsonify({'status_code': 200, 'message':response})

    @app.route('/last/<time>/<mag>')
    @app.route('/last/<time>')
    def getTime(time, mag=5.5):
        '''for now this is a super simple function that just uses the USGS API to
        get the last however many quakes. In a future release this will need to
        be improved to read out of our database'''
        #sanitize inputs
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
        # oof I just googled it and this is gonna be rough
        pass

    return app
