import psycopg2
from dotenv import load_dotenv
import os

'''these are tools designed for smothing away the challenges of working with
psycopg2 and just wory about writting sql. They will most likely not be
directly accessible from within our app. I need to look up the style guide, but
its possible that this should have __ __ around its name.'''


load_dotenv()


def connect():
    return psycopg2.connect(user=os.environ['toyUSER'],
                            password=os.environ["toyPASSWORD"],
                            host=os.environ["toyHOST"],
                            dbname=os.environ["toyNAME"],
                            port=5432)


def query_one(query):
    CONN = connect()
    curs = CONN.cursor()
    try:
        response = curs.execute(query)
        response = curs.fetchone()
    except:
        print('Query returned no result')
        curs.close()
        CONN.commit()
        return None
    curs.close()
    CONN.commit()
    CONN.close()
    return response


def query_all(query):
    CONN = connect()
    curs = CONN.cursor()
    try:
        response = curs.execute(query)
        response = curs.fetchall()
    except:
        print('Query returned no result')
        curs.close()
        CONN.commit()
        return None
    curs.close()
    CONN.commit()
    CONN.close()
    return response


def query(query):
    CONN = connect()
    curs = CONN.cursor()
    try:
        curs.execute(query)
    except:
        print('Query error')
    curs.close()
    CONN.commit()
    CONN.close()
