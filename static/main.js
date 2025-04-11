// Initialize the map
var map = L.map('map').setView([37.5, -95.5], 4);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Force map to re-render on window resize
window.addEventListener('resize', function() {
    setTimeout(function() {
        map.invalidateSize();
    }, 100); // Small delay to ensure DOM is ready
});

// Ensure map renders on initial load
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        map.invalidateSize();
    }, 100);
});

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

            // Preload images to avoid loading delays
            images.forEach(url => {
                var img = new Image();
                img.src = url;
            });

            // Set available times for TimeDimension
            if (times.length > 0) {
                map.timeDimension.setAvailableTimes(times, 'replace');
            } else {
                console.error('No times available for TimeDimension');
                return;
            }

            // Define fixed bounds for the overlay
            var bounds = [[25, -125], [50, -66]];

            // Create an ImageOverlay layer
            var imageOverlay = L.imageOverlay(images[0] || '', bounds, { opacity: 0.8 });
            imageOverlay.addTo(map);

            // Listen for time changes and update the image overlay
            map.timeDimension.on('timeload', function(data) {
                var time = new Date(data.time).toISOString();
                var idx = times.indexOf(time);
                console.log('Time changed to:', time, 'idx:', idx);
                if (idx >= 0) {
                    imageOverlay.setUrl(images[idx]);
                    console.log('Updated imageOverlay with URL:', images[idx]);
                }
            });

            // Initialize the TimeDimension player
            var player = new L.TimeDimension.Player({
                transitionTime: 200, // Faster transition for smoother playback
                loop: true,
                startOver: true
            }, timeDimension);

            // Add the TimeDimension control (slider)
            var timeControl = L.control.timeDimension({
                position: 'bottomleft',
                player: player,
                timeDimension: timeDimension,
                speedSlider: true,
                autoPlay: false
            });
            timeControl.addTo(map);

            // Force re-render of the control after a delay
            setTimeout(function() {
                timeControl._update(); // Force update of the control
                map.invalidateSize(); // Re-render the map
            }, 1000);

            // Set the initial time to the first timestamp
            if (times[0]) {
                map.timeDimension.setCurrentTime(new Date(times[0]).getTime());
            }

            // Force map to re-render after setting up layers
            setTimeout(function() {
                map.invalidateSize();
            }, 500);

            // Explicitly start the player after a delay
            setTimeout(function() {
                player.start();
            }, 1500);
        })
        .catch(error => {
            console.error('Error fetching radar data:', error);
            // Fallback: Ensure map is still visible even if data fails
            map.invalidateSize();
        });
}