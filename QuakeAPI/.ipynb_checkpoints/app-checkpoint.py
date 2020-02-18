from flask import Flask
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
    
    return app