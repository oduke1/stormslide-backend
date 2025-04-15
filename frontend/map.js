// Initialize the map
function initMap() {
    const map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 30.4383, lng: -84.2807 }, // Tallahassee, FL
        zoom: 9,
        mapTypeId: 'roadmap' // Options: 'roadmap', 'satellite', 'hybrid', 'terrain'
    });

    // Fetch tornado data
    fetch('/tornadoes')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(tornadoes => {
            console.log('Tornadoes:', tornadoes);

            tornadoes.forEach(tornado => {
                const position = { lat: tornado.latitude, lng: tornado.longitude };

                // Level II: Yellow circles
                if (tornado.source === 'Level II') {
                    new google.maps.Circle({
                        strokeColor: '#FFFF00',
                        strokeOpacity: 0.8,
                        strokeWeight: 2,
                        fillColor: '#FFFF00',
                        fillOpacity: 0.7,
                        map: map,
                        center: position,
                        radius: 800 // 8px equivalent in meters (approximate)
                    });
                }

                // Level III: TVS (red triangle) and MESO (orange square)
                if (tornado.source === 'Level III') {
                    const icon = {
                        url: tornado.type === 'TVS' ? 'https://your-domain.com/triangle.png' : 'https://your-domain.com/square.png',
                        scaledSize: new google.maps.Size(15, 15) // 15x15 pixels
                    };
                    const marker = new google.maps.Marker({
                        position: position,
                        map: map,
                        icon: icon
                    });

                    // Optional: Add info window for shear value
                    const infoWindow = new google.maps.InfoWindow({
                        content: `Shear: ${tornado.shear}`
                    });
                    marker.addListener('click', () => {
                        infoWindow.open(map, marker);
                    });
                }
            });
        })
        .catch(error => {
            console.error('Error fetching tornadoes:', error);
        });
}

// Ensure initMap is called after the API loads
window.initMap = initMap;