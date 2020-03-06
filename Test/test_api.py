import pytest
from QuakeAPI import APP


@pytest.fixture
def client():
    APP.config['TESTING'] = True
    with APP.test_client() as client:
        yield client


def test_base_route(client):
    response = client.get('/')
    print(response.data)
    message = b'{"message": "success, the flask API is running",
                 "status_code": 200}\n'
    assert message in response.data


def test_test_route(client):
    ''' this is actually testing the query_one function it occurs to me '''
    response = client.get('/test')
    print(response.data)
    message = b'[3, "5km WNW of Cobb, CA",
                 1582252014390, -122.776001, 38.8348351, 0.4, false]\n'
    assert message in response.data


def test_bad_time(client):
    response = client.get('/last/fail')
    test_message = 'please choose from \\"hour\\", \\"day\\",\\n\\"week\\", ' +
    'or \\"month\\"'
    message = b'{"message": test_message, "status_code": 400}\n'
    print(response.data)
    assert message in response.data
