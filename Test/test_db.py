import pytest
from QuakeAPI.DBQueries import *


def test_query_one():
    response = query_one('SELECT * FROM USGS where time=1582252014390')
    correct = (3, '5km WNW of Cobb, CA', 1582252014390, -122.776001,
               38.8348351, 0.4, False)
    assert response == correct


def test_query_all():
    response = query_all('SELECT * FROM USGS ORDER BY time ASC LIMIT 10;')
    # I'm sorry this looks so bad, my linter had a bad day
    correct = [(10, '13km WNW of Anza, CA', 1582250852330, -116.8098333,
                33.593, 0.82, False), (9, '10km NW of Pinnacles, CA',
                                       1582250901850, -121.2210007, 36.5906677,
                                       1.63, False),
               (8, '39km E of Cantwell, Alaska', 1582250949242, -148.1606,
                63.4412, 1.4, False), (7, '8km NW of The Geysers, CA',
                                       1582251133620, -122.8174973, 38.8339996,
                                       0.56, False),
               (6, '13km ESE of Volcano, Hawaii', 1582251291510,
                -155.1213379, 19.3811665, 2.02, False),
               (5, '44km WNW of Valdez, Alaska', 1582251787473, -147.0807,
                61.3088, 2.1, False), (4, '6km SSE of Pahala, Hawaii',
               1582251932400, -155.4631653, 19.1459999, 1.88, False),
               (3, '5km WNW of Cobb, CA', 1582252014390, -122.776001,
                38.8348351, 0.4, False), (2, '15km N of Morgan Hill, CA',
               1582253575500, -121.6496658, 37.2671661, 2.17, False),
               (1, '19km ESE of Anza, CA', 1582253953620, -116.4836667,
                33.4823333, 0.51, False)]
    assert response == correct
