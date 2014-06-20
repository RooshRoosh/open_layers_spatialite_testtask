
var map, building;
console.log('uploaded!')
function onload(){
    map = new OpenLayers.Map('map');

    var osm = new OpenLayers.Layer.OSM();
    map.addLayer(osm);

    building = new OpenLayers.Layer.Vector('Building', {
        strategies: [
            new OpenLayers.Strategy.BBOX(),
        ],
        protocol: new OpenLayers.Protocol.HTTP({
            url: '/building',
            format: new OpenLayers.Format.GeoJSON({
            })
        }),
//        eventListener : {
//            'updatesize' : clearBuildingAfterResize,
//            'zoomend': clearBuilddingAfrerZoomend
//        }
    });


    map.addLayer(building);



    map.setCenter(
        new OpenLayers.LonLat(60.6069, 56.8370).transform("EPSG:4326", "EPSG:900913"),
        15
    );

    map.events.register('zoomend', map, function(){
        building.destroyFeatures();
        console.log('zoomend')}
    );
//    map.events.register('updatesize', map, function(){console.log('updatesize')});
//    map.events.register("move", map, function() {console.log("panning");});
    map.events.register('zoomstart', map, function(){console.log('zoomstart')});
//
//
//    building.events.register("refresh", building, function(){console.log('refresh')});
//    building.events.register('move', building, function(){console.log('move')});
//    building.events.register('moveend', building, function(){
//            console.log('moveend');
//        }
//    );
//
//    building.events.register('loadstart', building, function(){console.log('loadstart')});
//    building.events.register('loadend', building, function(){console.log('loadend');});
//
//    building.events.register('sketchstarted', building, function(){console.log('sketchstarted');});
//    building.events.register('sketchmodified', building, function(){console.log('sketchmodified');});
//    building.events.register('sketchcomplete', building, function(){console.log('sketchcomplete');});

//    map.events.register()

//    map.events.register('moveend', map, function(){clearAfterMove(map, building)});
}