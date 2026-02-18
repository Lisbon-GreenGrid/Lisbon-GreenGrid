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
// --- FIND TREE BY ID LOGIC ---

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
