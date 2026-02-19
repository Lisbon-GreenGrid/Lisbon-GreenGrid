const API_BASE_URL = "http://localhost:5000";

// --- 1. MAP & BASEMAP INITIALIZATION ---

const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
});

const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
});

const darkMap = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 20
});

// Initialize the map
var map = new L.Map('leaflet', {
    center: [38.7448, -9.1607], // Lisbon coordinates
    zoom: 12.5,
    layers: [osm] // Default base layer
});

map.zoomControl.setPosition("bottomright");

// --- 1.2. LAYER MANAGEMENT ---

// Create the group for tree markers and add it to the map by default
const treeLayer = L.layerGroup().addTo(map);
// Define the Base Maps
const baseMaps = {
    "Standard": osm,
    "Satellite": satellite,
    "Dark Mode": darkMap
};
// Define the Overlays (The Trees)
const AllTrees = {
    "Tree Inventory": treeLayer
};
// One single control for both base maps and overlays
L.control.layers(baseMaps, AllTrees).addTo(map);

// --- 1.3. All Trees LOADING ---

function loadAllTrees() {
    fetch(`${API_BASE_URL}/trees`)
        .then(response => response.json())
        .then(data => {
            treeLayer.clearLayers();

            data.forEach(tree => {
                // Parse geometry
                const geom = JSON.parse(tree.geometry);
                const lat = geom.coordinates[1];
                const lon = geom.coordinates[0];

                const marker = L.circleMarker([lat, lon], {
                    radius: 6,
                    fillColor: "#2d5a27",
                    color: "#ffffff",
                    weight: 1,
                    fillOpacity: 0.9
                });

                marker.bindPopup(`
                    <div style="font-family: sans-serif;">
                        <h4 style="margin:0; color:#2d5a27;">${tree.nome_vulga}</h4>
                        <hr>
                        <b>ID:</b> ${tree.tree_id}<br>
                        <b>Species:</b> <i>${tree.especie}</i><br>
                        <b>Authority:</b> ${tree.manutencao}
                    </div>
                `);

                marker.addTo(treeLayer);
            });
        })
        .catch(err => console.error("Error loading trees:", err));
}

loadAllTrees();


// --- 2. SIDEBAR & UI LOGIC ---
const body = document.querySelector("body"),
    sidebar = body.querySelector(".sidebar"),
    toggle = body.querySelector(".toggle"),
    modeSwitch = body.querySelector(".toggle-switch"),
    modeText = body.querySelector(".mode-text"),
    searchInput = document.getElementById("searchInput");

// Toggle Sidebar Collapse
toggle.onclick = () => sidebar.classList.toggle("close");

// Dark Mode Toggle
modeSwitch.onclick = () => {
    body.classList.toggle("dark");
    modeText.innerText = body.classList.contains("dark") ? "Light Mode" : "Dark Mode";
};

// Accordion Menu Logic
document.querySelectorAll(".nav-link").forEach(link => {
    link.onclick = function() {
        let subMenu = this.closest(".menu-links").querySelector(".sub-menu");
        document.querySelectorAll(".sub-menu").forEach(menu => {
            if (menu !== subMenu) menu.style.display = "none";
        });
        subMenu.style.display = (subMenu.style.display === "block") ? "none" : "block";
    };
});


// --- 3. SECTION HANDLERS ---

// --- 3.1. SEARCH BY SPECIES OR FREGUESIA ---
// --- 1. POPULATE BOTH RECOMMENDATIONS ON LOAD ---
function setupRecommendations() {
    fetch(`${API_BASE_URL}/trees`)
        .then(res => res.json())
        .then(data => {
            // 1. Handle Species Recommendations
            const speciesDatalist = document.getElementById('treeNamesList');
            const uniqueSpecies = [...new Set(data.map(tree => tree.especie).filter(Boolean))];
            
            speciesDatalist.innerHTML = uniqueSpecies
                .map(name => `<option value="${name}">`)
                .join('');

            // 2. Handle Freguesia Recommendations
            const fregDatalist = document.getElementById('fregList');
            // Extract unique Freguesia names
            const uniqueFreg = [...new Set(data.map(tree => tree.freguesia).filter(Boolean))];
            
            fregDatalist.innerHTML = uniqueFreg
                .map(name => `<option value="${name}">`)
                .join('');
                
            console.log("Recommendations loaded for Species and Parishes!");
        })
        .catch(err => console.error("Could not load recommendations:", err));
}
// Call the function to populate both datalists on page load 
setupRecommendations();

// --- 2. COMBINED FILTER LOGIC ---
document.getElementById('filterBySpeciesORFraguesiaButton').onclick = function() {
    const speciesVal = document.getElementById('nameFilter').value.trim();
    const fregVal = document.getElementById('fregFilter').value.trim();

    let apiUrl = "";

    // Decide which API to hit based on which field has text
    if (speciesVal) {
        apiUrl = `${API_BASE_URL}/trees/species/${encodeURIComponent(speciesVal)}`;
    } else if (fregVal) {
        apiUrl = `${API_BASE_URL}/trees/freguesia/${encodeURIComponent(fregVal)}`;
    } else {
        alert("Please enter a Species name or a Parish (Freguesia)");
        return;
    }

    fetch(apiUrl)
        .then(res => res.json())
        .then(data => {
            if (data.length === 0) {
                alert("No trees found for this filter.");
                return;
            }

            // --- Clear the map and show only filtered results ---
            treeLayer.clearLayers();
            
            // Create a bounds object to zoom the map to fit all results
            const bounds = L.latLngBounds();

            data.forEach(tree => {
                const geom = JSON.parse(tree.geometry);
                const lat = geom.coordinates[1];
                const lon = geom.coordinates[0];
                const latLng = [lat, lon];

                const marker = L.circleMarker(latLng, {
                    radius: 7,
                    fillColor: "#3498db", // Different color (blue) for filtered results
                    color: "#fff",
                    weight: 2,
                    fillOpacity: 0.9
                });

                marker.bindPopup(`
                    <b>${tree.nome_vulga}</b><br>
                    ID: ${tree.tree_id}<br>
                    Freguesia: ${tree.freguesia}
                `);

                marker.addTo(treeLayer);
                bounds.extend(latLng); // Add point to bounds
            });

            // Zoom the map to fit all the markers found
            map.flyToBounds(bounds, { padding: [50, 50], duration: 1.5 });
        })
        .catch(err => console.error("Filter error:", err));
};


// --- 3.2. FIND TREE BY ID LOGIC ---
document.getElementById('findTreeButton').onclick = function() {
    const treeId = document.getElementById('idFilter').value;

    if (!treeId) {
        alert("Please enter a Tree ID");
        return;
    }

    fetch(`${API_BASE_URL}/tree/${treeId}`)
        .then(response => response.json())
        .then(tree => {
            if (tree.error) {
                alert("Tree not found!");
                return;
            }

            // --- Clear all other trees from the map ---
            treeLayer.clearLayers(); 

            const geom = JSON.parse(tree.geometry);
            const lat = geom.coordinates[1];
            const lon = geom.coordinates[0];

            // Create the single marker for the searched tree
            const marker = L.circleMarker([lat, lon], {
                radius: 8, // Slightly larger to make it stand out
                fillColor: "#e74c3c", // Red color to distinguish it from the green grid
                color: "#ffffff",
                weight: 2,
                fillOpacity: 1
            });

            // Add the single marker back to the layer so it stays toggleable
            marker.addTo(treeLayer);

            map.flyTo([lat, lon], 17, {
                animate: true,
                duration: 1.5
            });

            marker.bindPopup(`
                <div style="font-family: sans-serif; min-width: 180px;">
                    <h4 style="margin:0; color:#e74c3c;">Tree Found (ID: ${tree.tree_id})</h4>
                    <hr>
                    <b>Common Name:</b> ${tree.nome_vulga || 'N/A'}<br>
                    <b>Species:</b> <i>${tree.especie || 'N/A'}</i>
                </div>
            `).openPopup();
        })
        .catch(err => {
            console.error("Error finding tree:", err);
        });
};

// -- 3.3. NEAREST TREES LOGIC ---
document.getElementById('nearTreeButton').onclick = function() {
    const radius = document.getElementById('radiusFilter').value || 500;
    const status = document.getElementById('locationStatus');

    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser");
        return;
    }

    status.innerText = "Locating...";

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            status.innerText = `Found: ${lat.toFixed(4)}, ${lon.toFixed(4)}`;

            fetch(`${API_BASE_URL}/trees/near?lat=${lat}&lon=${lon}&radius=${radius}`)
                .then(res => res.json())
                .then(data => {
                    if (data.length === 0) {
                        alert("No trees found in this radius.");
                        return;
                    }

                    treeLayer.clearLayers();
                    const bounds = L.latLngBounds();

                    // 1. User Location
                    const userIcon = L.icon({
                        iconUrl: 'https://cdn-icons-png.flaticon.com/512/3595/3595598.png',
                        iconSize: [40, 40]
                    });
                    L.marker([lat, lon], {icon: userIcon}).addTo(treeLayer).bindPopup("<b>You are here</b>").openPopup();
                    bounds.extend([lat, lon]);

                    // 2. Search Radius Circle
                    const searchCircle = L.circle([lat, lon], {
                        radius: parseInt(radius),
                        color: '#2ecc71',
                        fillOpacity: 0.1, 
                        interactive: false
                    }).addTo(treeLayer);

                    // --- Include the entire circle in the map view ---
                    bounds.extend(searchCircle.getBounds());

                    // 3. Add found trees
                    data.forEach(tree => {
                        const geom = JSON.parse(tree.geometry);
                        const treeCoords = [geom.coordinates[1], geom.coordinates[0]];
                        
                        const marker = L.circleMarker(treeCoords, {
                            radius: 7,
                            fillColor: "#27ae60",
                            color: "#fff",
                            fillOpacity: 1
                        }).addTo(treeLayer);

                        marker.bindPopup(`
                            <b>${tree.nome_vulga}</b><br>
                            ID: ${tree.tree_id}<br>
                            <small>Species: ${tree.especie}</small>
                        `);
                        bounds.extend(treeCoords);
                    });

                    // --- DYNAMIC ZOOM: Automatically fits the radius and trees ---
                    map.flyToBounds(bounds, { 
                        padding: [50, 50], 
                        duration: 1.5,
                        maxZoom: 18 // Prevents it from zooming in too much on very small radii
                    });
                });
        },
        (error) => {
            status.innerText = "Unable to retrieve location.";
            alert("Error: " + error.message);
        }
    );
};


