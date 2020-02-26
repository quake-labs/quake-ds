''' this code is designed to run to test the lambda function without needing
to upload it to the lambda server every time'''
from Lambda_function.lambda_function import *
from QuakeAPI.DBQueries import query_all
import time

if __name__=='__main__':
    while True:
        print('starting insertion')
        pipe_data(HOUR)
        # for r in query_all('SELECT time, place FROM USGS ORDER BY time desc;'):
        #     print(r)
        time.sleep(60)
