
var map, building;
console.log('uploaded!')

var bbox = new OpenLayers.Strategy.BBOX();
bbox.invalidBounds = function(b){return true};

function onload(){
    map = new OpenLayers.Map('map');

    var osm = new OpenLayers.Layer.OSM();
    map.addLayer(osm);

    building = new OpenLayers.Layer.Vector('Building', {
        strategies: [
            bbox,
        ],
        protocol: new OpenLayers.Protocol.HTTP({
            url: '/building',
            format: new OpenLayers.Format.GeoJSON({
            })
        }),
    });


    map.addLayer(building);
    map.setCenter(
        new OpenLayers.LonLat(60.6069, 56.8370).transform("EPSG:4326", "EPSG:900913"),
        15
    );
    map.events.register('zoomend', map, function(){
        building.destroyFeatures();
        }
    );
};