
var map, building;
console.log('uploaded!')
function onload(){
    map = new OpenLayers.Map('map');

    var osm = new OpenLayers.Layer.OSM();
    map.addLayer(osm);

    building = new OpenLayers.Layer.Vector('Building', {
        strategies: [
//            new OpenLayers.Strategy.Fixed(),
            new OpenLayers.Strategy.BBOX(),
//            new OpenLayers.Strategy.Cluster()
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
}
