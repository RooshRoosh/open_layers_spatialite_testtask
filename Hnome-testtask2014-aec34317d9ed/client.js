
var map, building;
console.log('uploaded!')

var bbox = new OpenLayers.Strategy.BBOX();
bbox.invalidBounds = function(b){return true};

//function calculateBounds(boundsObject) {
//    if(boundsObject) {
//        boundsObject = this.getMapBounds();
//    };
//    var center = boundsObject.getCenterLonLat(),
//        dataWidth = boundsObject.getWidth() * 2, // 2 = bbox.ratio;
//        dataHeight = boundsObject.getHeight() * 2; // 2 = bbox.ratio;
//    return new OpenLayers.Bounds(
//        center.lon - (dataWidth / 2),
//        center.lat - (dataHeight / 2),
//        center.lon + (dataWidth / 2),
//        center.lat + (dataHeight / 2)
//    );
//};

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

//        var mapBounds = bbox.getMapBounds(map);
//        var conutFeatures = building.features.length,
//            featureList = [];
//
//        for (var i=0; i< conutFeatures; i++) {
//            var feature = building.features[i];
//            var featureBounds = bbox.getMapBounds(feature);
//
//            if (!(
//                (featureBounds.bottom > mapBounds.bottom) &&
//                (featureBounds.top < mapBounds.top) &&
//                (featureBounds.left > mapBounds.left) &&
//                (featureBounds.right < mapBounds.right))
//                ) {
//                featureList = featureList.concat(feature)
//            }
//        };
//        for (var i=0; i<featureList.length; i++){
//            building.removeFeatures(featureList[i])
//        };

    });
};