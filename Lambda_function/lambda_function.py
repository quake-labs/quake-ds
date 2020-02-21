import json
from USGSetl import pipe_data, HOUR

def lambda_handler(event, context):
    # I'm not actually going to set this up until I can push back to lambda
    pipe_data(HOUR)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
