mapboxgl.accessToken = 'pk.eyJ1IjoidmFzY294dSIsImEiOiJja2t1cWx6MDA0YXM1MnBwZHR3ZG1yd3M4In0.DjWAWToeVQesaJp2GZc5_A';

var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/light-v10',
    zoom: 13,
    center: [-73.892722, 40.81654]
});

map.on('load', function () {
    map.addSource('route', {
        'type': 'geojson',
        'data': {
            'type': 'Feature',
            'properties': {},
            'geometry': {
                'type': 'LineString',
                'coordinates': []
            }
        }
    });

    map.addSource('nyc', {
        type: 'vector',
        url: 'mapbox://vascoxu.nyc'
    });

    let colors = {
        property: "pm25",
        stops: [
            [0, "#8cb4aa"],
            [6.0, "#cacfb5"],
            [12.0, "#eccfa7"],
            [18.0, "#f0bfac"],
            [24.0, "#f18c7f"],
        ],
    };

    let average_color = {};
    Object.assign(average_color, colors);
    average_color.property = "average"+average_color.property;
    console.log(average_color.property);

    map.addLayer({
        id: "nyc",
        type: 'line',
        source: "nyc",
            'source-layer': "nyc",
            'layout': {
            'line-join': 'bevel',
            'line-cap': "round"
        },
        'paint': {
            'line-color': "#8cb4aa",
            'line-width': ['interpolate',['linear'],['zoom'],10,3,14,8],
        }
    });

    var segment_layer = "nyc";

    // Highlight segment on mouse-hover
    map.on('mouseenter', segment_layer, function(e) {
        feature = e.features[0];

        map.addSource('selectedRoad', {
            "type":"geojson",
            "data": feature.toJSON()
        });
        map.addLayer({
            "id": "selectedRoad",
            "type": "line",
            "source": "selectedRoad",
            "layout": {
                "line-join": "round",
                "line-cap": "round"
            },
            "paint": {
                "line-color": "white",
                "line-opacity": 0.5,
                "line-width": 8
            }
        });
    });

    // Unhighlight on mouse-leave
    map.on('mouseleave', segment_layer, function(e) {
        map.getCanvas().style.cursor = '';
        try {
            map.removeLayer('selectedRoad');
        } catch (e) {};
        try {
            map.removeSource('selectedRoad');
        } catch (e) {};
    });

    // Click listener for segment
    map.on('click', segment_layer, function(e) {
        // get coordinates of selected line
        feature = e.features[0];
        coordinates = feature.toJSON().geometry.coordinates;
        coords_size = coordinates.length;
        id = feature['id'];
        point1 = String(coordinates[0]).split(',').join(', ')
        point2 = String(coordinates[coords_size-1]).split(',').join(', ')

        document.getElementById('p1').textContent = point1;
        document.getElementById('p2').textContent = point2;
        document.getElementById('id').textContent = id;

        // set popup
        /*
        new mapboxgl.Popup()
        .setLngLat(e.lngLat)
        .setHTML("<b>Line</b> : " + "[" + point1 + "]" + " <br> to <br> " + "[" + point2 + "]")
        .addTo(map);
        */
    });        
});