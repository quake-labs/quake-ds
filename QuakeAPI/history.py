from flask import jsonify
from math import degrees, radians, cos, sin, asin, atan2, sqrt


def history(lat, lon, dist):
    '''Calculate the top left and bottom right coordinates at distance dist
    from coordinates lat, lon'''

    lat = radians(lat)
    lon = radians(lon)
    radius = 6371
    top_left = radians(315)
    bottom_right = radians(135)

    lat2A = asin(sin(lat) * cos(dist/radius) +
                 cos(lat) * sin(dist/radius) * cos(top_left))
    lat2B = asin(sin(lat) * cos(dist/radius) +
                 cos(lat) * sin(dist/radius) * cos(bottom_right))

    lon2A = lon + atan2(sin(top_left) * sin(dist/radius) *
                        cos(lat), cos(dist/radius) - sin(lat) * sin(lat2A))
    lon2B = lon + atan2(sin(bottom_right) * sin(dist/radius) *
                        cos(lat), cos(dist/radius) - sin(lat) * sin(lat2B))

    coordinates = {
        'lonA': degrees(lon2A),
        'latA': degrees(lat2A),
        'lonB': degrees(lon2B),
        'latB': degrees(lat2B)
    }


    return coordinates
