function initMap() {
    const map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 30.4383, lng: -84.2807 }, // Tallahassee, FL
        zoom: 9,
        mapTypeId: 'roadmap'
    });

    // Debounce function to limit rapid API calls
    const debounce = (func, wait) => {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func(...args), wait);
        };
    };

    const fetchTornadoes = debounce(() => {
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
                            url: tornado.type === 'TVS' ? 'https://stormslide-assets.s3.us-east-1.amazonaws.com/triangle.png' : 'https://stormslide-assets.s3.us-east-1.amazonaws.com/square.png',
                            scaledSize: new google.maps.Size(15, 15)
                        };
                        const marker = new google.maps.Marker({
                            position: position,
                            map: map,
                            icon: icon
                        });
                        const infoWindow = new google.maps.InfoWindow({
                            content: `
                                <div style="
                                    font-family: 'Helvetica Now', 'Roboto', 'Arial', sans-serif;
                                    background: linear-gradient(45deg, #FFD700, #FFA500); /* Glass-like gradient */
                                    color: #2E2E2E;
                                    padding: 10px;
                                    border-radius: 10px;
                                    text-transform: uppercase;
                                    font-weight: bold;
                                    letter-spacing: 1px;
                                ">
                                    <h3 style="margin: 0; font-size: 14px;">SHEAR: ${tornado.shear}</h3>
                                    <p style="margin: 5px 0 0; font-size: 12px;">TYPE: ${tornado.type}</p>
                                </div>
                            `
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
    }, 1000);

    const fetchWeather = debounce(() => {
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

                // Remove any existing weather div to avoid duplicates
                const existingWeatherDiv = document.getElementById('weather-info');
                if (existingWeatherDiv) existingWeatherDiv.remove();

                const weatherDiv = document.createElement('div');
                weatherDiv.id = 'weather-info';
                weatherDiv.style.position = 'absolute';
                weatherDiv.style.top = '60px'; // Below the title
                weatherDiv.style.right = '20px';
                weatherDiv.style.background = 'linear-gradient(45deg, #2E2E2E, #4A4A4A)'; // Leather-like texture
                weatherDiv.style.color = '#FFFFFF';
                weatherDiv.style.padding = '15px';
                weatherDiv.style.borderRadius = '15px';
                weatherDiv.style.fontFamily = 'Helvetica Now, Roboto, Arial, sans-serif';
                weatherDiv.style.fontWeight = 'bold';
                weatherDiv.style.textTransform = 'uppercase';
                weatherDiv.style.letterSpacing = '2px';
                weatherDiv.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.3)';
                weatherDiv.style.zIndex = '1000'; // Ensure it appears above the map
                weatherDiv.innerHTML = `
                    <div>TEMPERATURE: ${temperature}</div>
                    <div>CONDITION: ${condition}</div>
                    <div>LOCATION: TALLAHASSEE, FL</div>
                `;
                document.body.appendChild(weatherDiv);
            })
            .catch(error => {
                console.error('Error fetching weather data:', error);
            });
    }, 1000);

    const fetchRadarData = () => {
        return fetch('/radar')
            .then((response) => response.json())
            .then((radarData) => {
                console.log('Radar data:', radarData);
                return radarData;
            })
            .catch((error) => {
                console.error('Error fetching radar data:', error);
                return [];
            });
    };

    let radarMarkers = [];
    let radarTimeIndex = 0;
    let radarData = [];

    const updateRadarOverlay = (timeIndex) => {
        // Clear previous radar markers
        radarMarkers.forEach(marker => marker.setMap(null));
        radarMarkers = [];

        const currentData = radarData[timeIndex];
        if (!currentData || !currentData.stormcells) return;

        currentData.stormcells.forEach(storm => {
            const position = { lat: storm.loc.lat, lng: storm.loc.long };
            const marker = new google.maps.Marker({
                position: position,
                map: map,
                icon: {
                    url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                        <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 30 30">
                            <rect x="5" y="5" width="20" height="20" fill="#87CEEB" stroke="#FFFFFF" stroke-width="2" rx="5"/>
                        </svg>
                    `),
                    scaledSize: new google.maps.Size(30, 30)
                }
            });
            radarMarkers.push(marker);

            const infoWindow = new google.maps.InfoWindow({
                content: `
                    <div style="
                        font-family: 'Helvetica Now', 'Roboto', 'Arial', sans-serif;
                        background: linear-gradient(45deg, #FFD700, #FFA500); /* Glass-like gradient */
                        color: #2E2E2E;
                        padding: 10px;
                        border-radius: 10px;
                        text-transform: uppercase;
                        font-weight: bold;
                        letter-spacing: 1px;
                    ">
                        <h3 style="margin: 0; font-size: 14px;">STORM CELL</h3>
                        <p style="margin: 5px 0 0; font-size: 12px;">LAT: ${position.lat}, LON: ${position.lng}</p>
                        <p style="margin: 5px 0 0; font-size: 12px;">TIME: ${Math.abs(currentData.time)} MIN AGO</p>
                    </div>
                `
            });

            marker.addListener('click', () => {
                infoWindow.open(map, marker);
            });
        });
    };

    const createSlider = () => {
        // Remove any existing slider to avoid duplicates
        const existingSlider = document.getElementById('radar-slider');
        if (existingSlider) existingSlider.remove();

        const sliderContainer = document.createElement('div');
        sliderContainer.id = 'radar-slider';
        sliderContainer.style.position = 'absolute';
        sliderContainer.style.bottom = '20px';
        sliderContainer.style.left = '50%';
        sliderContainer.style.transform = 'translateX(-50%)';
        sliderContainer.style.background = 'linear-gradient(45deg, #8B4513, #D2691E)'; // Wood-like texture with brown/orange gradient
        sliderContainer.style.padding = '10px';
        sliderContainer.style.borderRadius = '15px';
        sliderContainer.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.3)';
        sliderContainer.style.width = '300px';
        sliderContainer.style.textAlign = 'center';
        sliderContainer.style.zIndex = '1000'; // Ensure it appears above the map

        const sliderLabel = document.createElement('div');
        sliderLabel.textContent = 'RADAR TIME';
        sliderLabel.style.fontFamily = 'Helvetica Now, Roboto, Arial, sans-serif';
        sliderLabel.style.fontWeight = 'bold';
        sliderLabel.style.color = '#FFFFFF';
        sliderLabel.style.textTransform = 'uppercase';
        sliderLabel.style.letterSpacing = '2px';
        sliderLabel.style.marginBottom = '10px';

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = '0';
        slider.max = radarData.length - 1;
        slider.value = radarTimeIndex;
        slider.style.width = '80%';
        slider.style.accentColor = '#FF6F61'; // Vibrant coral for the slider
        slider.style.background = '#2E2E2E'; // Dark gray track
        slider.style.height = '8px';
        slider.style.borderRadius = '5px';
        slider.style.cursor = 'pointer';

        slider.oninput = (e) => {
            radarTimeIndex = parseInt(e.target.value);
            updateRadarOverlay(radarTimeIndex);
        };

        sliderContainer.appendChild(sliderLabel);
        sliderContainer.appendChild(slider);
        document.body.appendChild(sliderContainer);
    };

    const createTitle = () => {
        // Remove existing h1 to replace with styled title
        const existingTitle = document.querySelector('h1');
        if (existingTitle) existingTitle.remove();

        const title = document.createElement('div');
        title.textContent = 'STORMSLIDE TORNADO MAP';
        title.style.position = 'absolute';
        title.style.top = '20px';
        title.style.left = '20px';
        title.style.fontFamily = 'Helvetica Now, Roboto, Arial, sans-serif';
        title.style.fontWeight = 'bold';
        title.style.fontSize = '24px';
        title.style.color = '#FFD700'; // Golden yellow for vibrancy
        title.style.textTransform = 'uppercase';
        title.style.letterSpacing = '3px';
        title.style.textShadow = '2px 2px 4px rgba(0, 0, 0, 0.5)';
        title.style.zIndex = '1000'; // Ensure it appears above the map
        document.body.appendChild(title);
    };

    // Initial fetch calls
    fetchTornadoes();
    fetchWeather();

    // Initialize radar overlay
    fetchRadarData().then(data => {
        radarData = data;
        if (radarData.length > 0) {
            createSlider();
            updateRadarOverlay(radarTimeIndex);
        }
    });

    createTitle();
}

window.initMap = initMap;