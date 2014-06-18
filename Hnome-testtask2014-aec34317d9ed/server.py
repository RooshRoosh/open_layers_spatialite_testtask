# This Python file uses the following encoding: utf-8
from bottle import route, hook, response, request, run
import apsw
import json

@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@route('/building', method=['OPTIONS', 'GET'])
def building():
    con = apsw.Connection('data.sqlite')
    con.enableloadextension(True)
    #Укажите здесь свой путь до libspatialite
    # con.loadextension('/usr/lib/libspatialite.so')
    con.loadextension('/usr/local/Cellar/libspatialite/4.1.1/libspatialite.5')

    con.enableloadextension(False)
    
    c = con.cursor()
    c.execute('SELECT AsGeoJSON(Geometry) FROM building')
    features  = c.fetchall()
    con.close()
    
    
    res = {'type':'FeatureCollection','features':[]}
    for vals in features:
        res['features'].append({'type':'Feature', 'geometry':json.loads(vals[0])})
    
    return json.dumps(res)

if __name__ == "__main__":
    run(host='localhost', port=8088)
