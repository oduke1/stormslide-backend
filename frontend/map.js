// frontend/map.js
const map = new maplibregl.Map({
    container: 'map',
    style: {
        version: 8,
        sources: {
            osm: {
                type: 'raster',
                tiles: ['https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'],
                tileSize: 256,
                attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            }
        },
        layers: [{
            id: 'osm',
            type: 'raster',
            source: 'osm',
            minzoom: 0,
            maxzoom: 18
        }]
    },
    center: [-84.2807, 30.4383], // Tallahassee, FL (KTLH)
    zoom: 7
});

map.on('load', async () => {
    const response = await fetch('https://stormslide.net/tornadoes');
    const tornadoes = await response.json();
    console.log('Tornadoes:', tornadoes);

    map.addSource('tornadoes', {
        type: 'geojson',
        data: {
            type: 'FeatureCollection',
            features: tornadoes.map(t => ({
                type: 'Feature',
                geometry: { type: 'Point', coordinates: [t.lon, t.lat] },
                properties: { shear: t.shear, type: t.type, source: t.source, time: t.time }
            }))
        }
    });

    map.addLayer({
        id: 'level2-layer',
        type: 'circle',
        source: 'tornadoes',
        filter: ['==', ['get', 'source'], 'Level II'],
        paint: {
            'circle-radius': 8,
            'circle-color': '#ffff00',
            'circle-opacity': 0.7
        }
    });

    map.addLayer({
        id: 'level3-tvs',
        type: 'circle',
        source: 'tornadoes',
        filter: ['all', ['==', ['get', 'source'], 'Level III'], ['==', ['get', 'type'], 'TVS']],
        paint: {
            'circle-radius': 10,
            'circle-color': '#ff0000',
            'circle-opacity': 0.8
        }
    });

    map.addLayer({
        id: 'level3-meso',
        type: 'circle',
        source: 'tornadoes',
        filter: ['all', ['==', ['get', 'source'], 'Level III'], ['==', ['get', 'type'], 'MESO']],
        paint: {
            'circle-radius': 8,
            'circle-color': '#ffa500',
            'circle-opacity': 0.8
        }
    });

    map.on('click', 'level2-layer', (e) => {
        const props = e.features[0].properties;
        new maplibregl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(`Potential Tornado<br>Shear: ${props.shear} m/s<br>Time: ${props.time || 'Unknown'}`)
            .addTo(map);
    });

    map.on('click', 'level3-tvs', (e) => {
        const props = e.features[0].properties;
        new maplibregl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(`Confirmed TVS<br>Shear: ${props.shear} m/s<br>Time: ${props.time || 'Unknown'}`)
            .addTo(map);
    });

    map.on('click', 'level3-meso', (e) => {
        const props = e.features[0].properties;
        new maplibregl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(`Mesocyclone<br>Shear: ${props.shear} m/s<br>Time: ${props.time || 'Unknown'}`)
            .addTo(map);
    });

    map.on('mouseenter', 'level2-layer', () => map.getCanvas().style.cursor = 'pointer');
    map.on('mouseleave', 'level2-layer', () => map.getCanvas().style.cursor = '');
    map.on('mouseenter', 'level3-tvs', () => map.getCanvas().style.cursor = 'pointer');
    map.on('mouseleave', 'level3-tvs', () => map.getCanvas().style.cursor = '');
    map.on('mouseenter', 'level3-meso', () => map.getCanvas().style.cursor = 'pointer');
    map.on('mouseleave', 'level3-meso', () => map.getCanvas().style.cursor = '');
});