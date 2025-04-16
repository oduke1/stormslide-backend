function initMap() {
    const map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 30.4383, lng: -84.2807 }, // Tallahassee, FL
        zoom: 9,
        mapTypeId: 'roadmap'
    });

    fetch('/tornadoes')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(tornadoes => {
            console.log('Tornadoes:', tornadoes);
            tornadoes.forEach(tornado => {
                const position = { lat: tornado.latitude, lng: tornado.longitude };
                if (tornado.source === 'Level II') {
                    new google.maps.Circle({
                        strokeColor: '#FFFF00',
                        strokeOpacity: 0.8,
                        strokeWeight: 2,
                        fillColor: '#FFFF00',
                        fillOpacity: 0.7,
                        map: map,
                        center: position,
                        radius: 800
                    });
                }
                if (tornado.source === 'Level III') {
                    const icon = {
                        url: tornado.type === 'TVS' ? 'https://your-domain.com/triangle.png' : 'https://your-domain.com/square.png',
                        scaledSize: new google.maps.Size(15, 15)
                    };
                    const marker = new google.maps.Marker({
                        position: position,
                        map: map,
                        icon: icon
                    });
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

    fetch('/proxy-weather')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(weather => {
            console.log('Weather response:', weather);
            const dataSource = weather.response?.[0]?.periods?.[0] || weather.response?.[0]?.ob || weather.response?.[0] || {};
            const temperature = dataSource.tempC ? `${dataSource.tempC}°C` : 'N/A';
            const condition = dataSource.weather || 'N/A';
            console.log('Parsed temperature:', temperature, 'Condition:', condition);
            const weatherInfo = new google.maps.InfoWindow({
                content: `Current Weather in Tallahassee, FL:<br>Temperature: ${temperature}<br>Condition: ${condition}`,
                position: { lat: 30.4383, lng: -84.2807 }
            });
            weatherInfo.open(map);
        })
        .catch(error => {
            console.error('Error fetching weather data:', error);
        });
}

window.initMap = initMap;