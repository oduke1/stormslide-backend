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
            var images = data.forecast.map(f => f.image);
            console.log('Times:', times);
            console.log('Images:', images);

            // Set available times for TimeDimension
            map.timeDimension.setAvailableTimes(times, 'replace');

            // Create an ImageOverlay layer
            var imageOverlay = L.imageOverlay(images[0] || '', [[25, -125], [50, -66]], { opacity: 0.8 });
            imageOverlay.addTo(map);

            // Listen for time changes and update the image overlay
            map.timeDimension.on('timeload', function(data) {
                var time = new Date(data.time).toISOString();
                var idx = times.indexOf(time);
                console.log('Time changed to:', time, 'idx:', idx);
                if (idx >= 0) {
                    // Remove and re-add the overlay to ensure consistent rendering
                    imageOverlay.remove();
                    imageOverlay = L.imageOverlay(images[idx], [[25, -125], [50, -66]], { opacity: 0.8 });
                    imageOverlay.addTo(map);
                    console.log('Updated imageOverlay with URL:', images[idx]);
                }
            });

            // Initialize the TimeDimension player
            var player = new L.TimeDimension.Player({
                transitionTime: 500, // 0.5 second transition
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

            // Set the initial time to the first timestamp
            map.timeDimension.setCurrentTime(new Date(times[0]).getTime());
        })
        .catch(error => console.error('Error fetching radar data:', error));
}