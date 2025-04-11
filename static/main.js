// Initialize the map
var map = L.map('map').setView([39.8283, -98.5795], 4);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Check if L.timeDimension is available
if (typeof L.timeDimension === 'undefined') {
    console.error('L.timeDimension is not defined. Ensure Leaflet-TimeDimension loaded correctly.');
} else {
    // Initialize TimeDimension
    var timeDimension = new L.TimeDimension({
        period: "PT24H" // 24-hour intervals
    });
    map.timeDimension = timeDimension;

    // Fetch radar data
    fetch('/radar')
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch radar data');
            return response.json();
        })
        .then(data => {
            console.log('Radar data:', data);

            // Extract times and images from the forecast data
            var times = data.forecast.map(f => new Date(f.timestamp).toISOString());
            var images = data.forecast.map(f => `/radar/image/${f.image}`);
            console.log('Times:', times);
            console.log('Images:', images);

            // Set available times for TimeDimension
            map.timeDimension.setAvailableTimes(times, 'replace');

            // Create an ImageOverlay layer
            var imageOverlay = L.imageOverlay('', [[25, -125], [50, -66]]);

            // Wrap the ImageOverlay with L.timeDimension.layer
            var radarLayer = L.timeDimension.layer(imageOverlay, {
                updateTimeDimension: true,
                setDefaultTime: true,
                getUrl: function(time) {
                    var idx = times.indexOf(time);
                    console.log('Fetching image for time:', time, 'idx:', idx);
                    return idx >= 0 ? images[idx] : '';
                }
            });

            // Add the radar layer to the map
            radarLayer.addTo(map);

            // Initialize the TimeDimension player
            var player = new L.TimeDimension.Player({
                transitionTime: 1000, // 1 second transition
                loop: true,
                startOver: true
            }, timeDimension);

            // Add the TimeDimension control (slider)
            L.control.timeDimension({
                position: 'bottomleft',
                player: player,
                timeDimension: timeDimension,
                speedSlider: true,
                autoPlay: false
            }).addTo(map);
        })
        .catch(error => console.error('Error fetching radar data:', error));
}