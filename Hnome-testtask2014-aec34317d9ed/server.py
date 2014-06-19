# This Python file uses the following encoding: utf-8
from bottle import route, hook, response
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

@route('/building', method=['OPTIONS', 'GET'])
def building():
    con = apsw.Connection('data.sqlite')
    con.enableloadextension(True)
    con.loadextension('/usr/lib/x86_64-linux-gnu/libspatialite.so.5')
    con.enableloadextension(False)
    
    c = con.cursor()
    c.execute('SELECT AsGeoJSON(Geometry) FROM building')
    features  = c.fetchall()
    con.close()

    res = {'type':'FeatureCollection','features':[]}
    for vals in features:
        res['features'].append({'type':'Feature', 'geometry':json.loads(vals[0])})
    
    return json.dumps(res)

app = application = bottle.default_app()

