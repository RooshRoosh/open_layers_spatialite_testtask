# This Python file uses the following encoding: utf-8
from bottle import route, hook, response, request
from bottle import template
import bottle

import apsw
import json



@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@route('/', method=['GET'])
def index():
    return template('index')

@route('/building', method=['GET'])
def building():
    con = apsw.Connection('data.sqlite')
    con.enableloadextension(True)
    con.loadextension('/usr/lib/x86_64-linux-gnu/libspatialite.so.5')
    con.enableloadextension(False)

    c = con.cursor()
    bbox = request.params['bbox'].split(',')

    res = {'type':'FeatureCollection','features':[]}
    for vals in c.execute('''
        SELECT AsGeoJSON(Geometry)
        FROM building
        WHERE ROWID IN (SELECT pkid
              FROM idx_building_Geometry
              WHERE xmin >= ? AND
                    xmax <= ? AND
                    ymin >= ? AND
                    ymax <= ?
               )
        ''', (bbox[0],bbox[2], bbox[1], bbox[3])):
        res['features'].append({'type':'Feature', 'geometry':json.loads(vals[0])})

    return json.dumps(res)

@route('/clusters', method=['GET'])
def building():
    con = apsw.Connection('data.sqlite')
    con.enableloadextension(True)
    con.loadextension('/usr/lib/x86_64-linux-gnu/libspatialite.so.5')
    con.enableloadextension(False)
    c = con.cursor()
    res = {'type':'FeatureCollection','features':[]}

    for vals in c.execute('''
    SELECT AsGeoJSON(Geometry)
    FROM clusters'''):
        res['features'].append({'type':'Feature', 'geometry':json.loads(vals[0])})

    return json.dumps(res)

app = application = bottle.default_app()