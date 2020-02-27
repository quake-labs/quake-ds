import os
import tempfile

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
    message = b'{"message":"success, the flask API is running","status_code":200}\n'
    assert message in response.data
