#!/usr/bin/env python
'''Utilities for geocoding city names using PlaceFinder.

Example browser request:
http://where.yahooapis.com/geocode?q=Portland&appid=faypaS6k&flags=J

Python Yahoo! REST examples:
http://developer.yahoo.com/python/python-rest.html

geopy:
http://groups.google.com/group/geopy/browse_thread/thread/d06d5a2aefb0e63b
'''
import json
import urllib

import httplib2


def get_lat_long(location, appid = 'faypaS6k'):
    http = httplib2.Http()
    
    url = 'http://where.yahooapis.com/geocode?'

    params = urllib.urlencode({
        'appid': appid,
        'q': location,
        'flags': 'JC'
    })

    response, content = http.request(url + params, 'GET')
    print location, response, content
    content_json = json.loads(content)
    resultset = content_json["ResultSet"]

    assert resultset["Error"] == 0
    assert resultset["Found"] == 1
    result = resultset["Results"][0]

    return {
            "Latitude": result["latitude"],
            "Longitude": result["longitude"]
    }