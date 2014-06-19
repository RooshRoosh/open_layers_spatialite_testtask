/**
 * Created with PyCharm.
 * User: dns
 * Date: 19.06.14
 * Time: 20:50
 * To change this template use File | Settings | File Templates.
 */

var map
console.log('uploaded!')

function onload(){
    map = new OpenLayers.Map('map');
    console.log('created map!');

    var osm = new OpenLayers.Layer.OSM();
    console.log('created osm!');

    map.addLayer(osm);
    console.log('add osm to map!');

    map.setCenter(new OpenLayers.LonLat(60.6069, 56.8370).transform("EPSG:4326", "EPSG:900913"), 16);
    console.log('set center!');
}
