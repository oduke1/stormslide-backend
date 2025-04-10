var map = L.map('map').setView([39.8283, -98.5795], 4);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

fetch('/radar')
    .then(response => {
        if (!response.ok) throw new Error('Failed to fetch radar data');
        return response.json();
    })
    .then(data => {
        var radarLayers = data.forecast.map(f => {
            return {
                layer: L.imageOverlay(`/radar/image/${f.image}`, [[25, -125], [50, -66]]),
                time: new Date(f.timestamp).toISOString()
            };
        });

        map.timeDimension = new L.TimeDimension({
            times: radarLayers.map(l => l.time),
            currentTime: new Date(radarLayers[0].time)
        });

        var player = new L.TimeDimension.Player({
            transitionTime: 1000,
            loop: true
        }, map.timeDimension);

        var overlayMaps = {};
        radarLayers.forEach((rl, idx) => {
            overlayMaps[`Forecast ${idx}`] = rl.layer;
        });

        L.control.timeDimension({
            position: 'bottomleft',
            player: player,
            timeDimension: map.timeDimension,
            speedSlider: true
        }).addTo(map);

        radarLayers[0].layer.addTo(map);
        L.control.layers(null, overlayMaps).addTo(map);
    })
    .catch(error => console.error('Error fetching radar data:', error));