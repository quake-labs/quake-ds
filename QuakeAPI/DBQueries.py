import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

#This needs to be switched to connect to the postgreSQL DB
CONN = psycopg2.connect(user = os.getenv('toyUSER'),
                        password = os.getenv("toyPASSWORD"),
                        host = os.getenv("toyHOST"),
                        dbname = os.getenv("toyNAME"),
                        port = 5432)


def query_one(query):
    curs = CONN.cursor()
    try:
        response = curs.execute(query).fetchone()
    except:
        print('Query returned no result')
        curs.close()
        CONN.commit()
        return None
    curs.close()
    CONN.commit()
    return response

def query_all(query):
    curs = CONN.cursor()
    response = curs.execute(query)
    response = response.fetchall()
    curs.close()
    CONN.commit()
    return response

def query(query):
    curs = CONN.cursor()
    try:
        curs.execute(query)
    except:
        print('Query error')
    curs.close()
    CONN.commit()
