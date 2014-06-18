var map, building;

function onload(){
    map = new OpenLayers.Map('map');
    
    var osm = new OpenLayers.Layer.OSM();
    map.addLayer(osm);
    
    building = new OpenLayers.Layer.Vector('Building', {
        strategies: [new OpenLayers.Strategy.Fixed()],
        protocol: new OpenLayers.Protocol.HTTP({
            url: 'http://localhost:8088/building',
            format: new OpenLayers.Format.GeoJSON({
            })
        }),
    });
    map.addLayer(building);
    
    map.setCenter(new OpenLayers.LonLat(60.6069, 56.8370).transform("EPSG:4326", "EPSG:900913"), 16);
}
