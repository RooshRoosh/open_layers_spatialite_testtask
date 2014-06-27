
var map, building,
    getParams = OpenLayers.Util.getParameters(window.location.href);

getParams['mode'] = getParams['mode'] || 'building';

var bbox = new OpenLayers.Strategy.BBOX();
bbox.invalidBounds = function(b){return true};

function onload(){
    map = new OpenLayers.Map('map');

    var osm = new OpenLayers.Layer.OSM();
    map.addLayer(osm);

    var colors = [
        '#ffaaff', '#aaaaff',
        '#aaffff', '#aaffaa',
        '#ffffaa', '#ffaaaa'
    ]
    var context = {
        getColor: function(feature) {
            return colors[parseInt(Math.random()*5)]
        }// можно подумать о раскраске в 4 цвета
    };
    var template = {
        fillColor: "${getColor}", // using context.getColor(feature)
        fillOpacity: 0.9,
        strokeColor: "#c00",
        strokeOpacity: 1,
        strokeWidth: 1
    };

    building = new OpenLayers.Layer.Vector('Building', {
        strategies: [
            bbox,
        ],
        protocol: new OpenLayers.Protocol.HTTP({
            url: location.origin+'/'+getParams['mode'],
            format: new OpenLayers.Format.GeoJSON({
            })
        }),
        styleMap: new OpenLayers.Style(template, {context: context})
    });

    map.addLayer(building);
    map.setCenter(
        new OpenLayers.LonLat(60.6069, 56.8370).transform("EPSG:4326", "EPSG:900913"),
        15
    );
};

