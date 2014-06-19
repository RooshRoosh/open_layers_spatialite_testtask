# This Python file uses the following encoding: utf-8
from bottle import route, hook, response, request, run
from bottle import template, static_file
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

# @route('/ol/<staticfile>')
# def static(staticfile):
#     print staticfile
#     return static_file(staticfile,  root='ol')
#
# @route('/ol/img/<staticfile>')
# def static(staticfile):
#     print staticfile
#     return static_file(staticfile,  root='ol/img/')
#
# @route('/ol/theme/default/<staticfile>')
# def static(staticfile):
#     print staticfile
#     return static_file(staticfile,  root='ol/theme/default/')
#
# @route('/ol/theme/default/img/<staticfile>')
# def static(staticfile):
#     print staticfile
#     return static_file(staticfile,  root='ol/theme/default/img/')
#
# @route('/client.js')
# def static(staticfile):
#     return static_file('client.js',  root='')

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

