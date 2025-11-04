// --- 1. Map Initialization ---

// ALL Coordinates
const junctionCoordinates = {
    'Koramangala': [12.9357, 77.6245],
    'Silk Board': [12.9176, 77.6221],
    'Marath_W': [12.9569, 77.7011],  
    'Marath_E': [12.9575, 77.7030],  
    'Hebbal': [13.0382, 77.5919],
    'Elec_City': [12.8452, 77.6602], 
    'Yeshwantpur': [13.0233, 77.5515],
    'Majestic': [12.9767, 77.5713],
    'Indiranagar': [12.9719, 77.6411],
    'Whitefield': [12.9698, 77.7499],
    'Jayanagar': [12.9293, 77.5829]
};

const map = L.map('map').setView([12.9716, 77.5946], 11);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

for (const [name, coords] of Object.entries(junctionCoordinates)) {
    L.marker(coords).addTo(map).bindPopup(name.replace('_', ' '));
}

// --- 2. Global Variables ---
let routeLayer = null; 
let trafficLayerGroup = L.layerGroup().addTo(map);
// (All marker and click-state variables are removed)

// --- 3. Get UI Element References ---
const startSelect = document.getElementById('start-point');
const endSelect = document.getElementById('end-point');
// Get new result spans
const resultPath = document.getElementById('result-path');
const resultTime = document.getElementById('result-time');

// --- 4. NEW: Add Event Listeners ---
// This makes the app update automatically
startSelect.addEventListener('change', findRoute);
endSelect.addEventListener('change', findRoute);

async function findRoute() {
    // Read values from the dropdowns
    const start = startSelect.value;
    const end = endSelect.value;

    // Don't run if either dropdown is not selected
    if (!start || !end) {
        return;
    }

    if (start === end) {
        resultPath.textContent = 'Start and end points cannot be the same!';
        resultTime.textContent = '---';
        return;
    }
    
    resultPath.textContent = 'Calculating...';
    resultTime.textContent = '...';
    
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/get-route?start=${start}&end=${end}`);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Could not find route');
        }
        const data = await response.json();
        
        // --- UPDATED: Populate new results box ---
        resultPath.textContent = data.path.join(' → ');
        resultTime.textContent = `${data.time_minutes} minutes`;
        
        // Draw the route on the map
        drawRouteOnMap(data.path);

    } catch (error) {
        console.error('Error fetching route:', error);
        resultPath.textContent = `Error: ${error.message}`;
        resultTime.textContent = '---';
    }
}

function drawRouteOnMap(path) {
    if (routeLayer) {
        routeLayer.remove();
    }
    const routeCoordinates = path.map(junctionName => junctionCoordinates[junctionName]);
    routeLayer = L.polyline(routeCoordinates, {
        color: '#007bff',
        weight: 6,
        opacity: 0.8,
        dashArray: '10, 10'
    }).addTo(map);
    
    routeLayer.bringToFront();
    map.fitBounds(routeLayer.getBounds());
}

// --- 5. Live Traffic Visualization (Unchanged) ---
// This logic stays the same and will run in the background!

function getTrafficColor(liveTime, baseTime) {
    if (baseTime <= 0) return 'grey'; 
    const delayFactor = liveTime / baseTime;
    if (delayFactor < 1.2) {
        return '#28a745'; // Green
    } else if (delayFactor < 1.8) {
        return '#ffc107'; // Yellow
    } else {
        return '#dc3545'; // Red
    }
}

async function updateTrafficView() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/get-all-traffic');
        if (!response.ok) return;

        const data = await response.json();
        trafficLayerGroup.clearLayers();

        data.roads.forEach(road => {
            const startCoords = junctionCoordinates[road.start];
            const endCoords = junctionCoordinates[road.end];
            
            if (!startCoords || !endCoords) return;

            const color = getTrafficColor(road.live_time, road.base_time);
            
            L.polyline([startCoords, endCoords], {
                color: color,
                weight: 4,
                opacity: 0.6
            }).addTo(trafficLayerGroup);
        });

        if (routeLayer) {
            routeLayer.bringToFront();
        }

    } catch (error) {
        console.error('Error fetching all traffic:', error);
    }
}

// Start the Live Updater
setInterval(updateTrafficView, 10000);
updateTrafficView();