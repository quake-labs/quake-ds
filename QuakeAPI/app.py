from flask import Flask, jsonify
from .USGSetl import *


def create_app():
    app = Flask(__name__)

    @app.route('/lastQuake')
    def lastQuake():
        curs = CONN.cursor()
        response = curs.execute('''
            SELECT * FROM USGS
            ORDER BY Time Desc
            limit 1;
        ''')
        quake = response.fetchone()[0]
        return quake

    @app.route('/last/<time>')
    def getTime(time):
        '''for now this is a super simple function that just uses the USGS API to
        get the last however many quakes. In a future release this will need to
        be improved to read out of our database'''
        if time.upper() not in ['HOUR', 'DAY','WEEK','MONTH']:
            return 'Please select from hour, day, week, or month'
        else:
            return jsonify(get_recent_quakes(time))

    @app.route('/history/<lat>,<lon>,<dist>')
    def history(lat, lon, dist):
        #oof I just googled it and this is gonna be rough
        pass

    return app
