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
                        <b>Common Name:</b> ${tree.nome_vulga}<br>
                        <b>Species:</b> <i>${tree.especie}</i><br>
                        <b>Typology:</b> ${tree.tipologia}<br>
                        <b>PAP:</b> ${tree.pap}<br>
                        <b>Authority:</b> ${tree.manutencao}<br>
                        <b>Occupation:</b> ${tree.ocupacao}<br>
                        <b>Local:</b> ${tree.local}<br>
                        <b>Address:</b> ${tree.morada}<br>
                        <b>Freguesia:</b> ${tree.freguesia}
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

// -- 3.4. CREATE NEW TREE LOGIC ---
document.getElementById('createTreeButton').onclick = async function() {
    // 1. Gather data from the input fields
    const payload = {
        tree_id: document.getElementById('treeid').value,
        nome_vulga: document.getElementById('name').value,
        especie: document.getElementById('especie').value,
        tipologia: document.getElementById('tipologia').value,
        freguesia: document.getElementById('freg').value,
        lon: parseFloat(document.getElementById('lon').value),
        lat: parseFloat(document.getElementById('lat').value)
    };

    // 2. Basic Validation
    if (!payload.tree_id || !payload.lat || !payload.lon) {
        alert("Please fill in at least the Tree ID, Latitude, and Longitude.");
        return;
    }

    try {
        // 3. Send the POST request to your Flask API
        const response = await fetch(`${API_BASE_URL}/tree`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message); // "Tree created successfully"
            
            // 4. Update the map: add the new tree marker immediately
            const marker = L.circleMarker([payload.lat, payload.lon], {
                radius: 7,
                fillColor: "#27ae60",
                color: "#fff",
                weight: 2,
                fillOpacity: 1
            }).addTo(treeLayer);

            marker.bindPopup(`<b>${payload.nome_vulga}</b><br>ID: ${payload.tree_id} (New)`);
            
            // 5. Center map on the new tree
            map.flyTo([payload.lat, payload.lon], 17);

            // Clear form fields after success
            document.querySelectorAll('.sub-menu input').forEach(input => input.value = '');
        } else {
            alert("Error: " + (result.error || "Failed to create tree."));
        }
    } catch (error) {
        console.error("Create Tree Error:", error);
        alert("Could not connect to the database.");
    }
};

// -- 3.5. UPDATE TREE LOGIC ---
document.getElementById('updateTreeButton').onclick = async function() {
    const container = this.closest('.sub-menu');
    const treeId = container.querySelector('#treeid').value;
    
    // Gather updated data
    const payload = {
        nome_vulga: container.querySelector('#name').value,
        especie: container.querySelector('#especie').value,
        tipologia: container.querySelector('#tipologia').value,
        morada: container.querySelector('#morada').value,
        pap: container.querySelector('#pap').value,
        manutencao: container.querySelector('#manutencao').value
    };

    if (!treeId) {
        alert("Please enter a Tree ID to update.");
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/tree/${treeId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message);

            // 1. Clear the map to focus on the edit
            treeLayer.clearLayers();

            // 2. Fetch the specific updated tree to get its current geometry
            const detailRes = await fetch(`${API_BASE_URL}/tree/${treeId}`);
            const tree = await detailRes.json();
            
            if (!tree.error) {
                const geom = JSON.parse(tree.geometry);
                const lat = geom.coordinates[1];
                const lon = geom.coordinates[0];

                // 3. Add the updated tree with a different color
                const updatedMarker = L.circleMarker([lat, lon], {
                    radius: 9, 
                    fillColor: "#e67e22",
                    color: "#fff",
                    weight: 2,
                    fillOpacity: 1
                }).addTo(treeLayer);

                // 4. Update Popup to show the new data
                updatedMarker.bindPopup(`
                    <div style="font-family: sans-serif;">
                        <h4 style="margin:0; color:#e67e22;">Updated Tree #${tree.tree_id}</h4>
                        <hr>
                        <b>New Name:</b> ${payload.nome_vulga}<br>
                        <b>New Species:</b> ${payload.especie}
                    </div>
                `).openPopup();

                // 5. Zoom to the point
                map.flyTo([lat, lon], 18);
            }
        } else {
            alert("Error: " + (result.error || "Update failed"));
        }
    } catch (error) {
        console.error("Update Error:", error);
        alert("Could not connect to the server.");
    }
};

// -- 3.6. DELETE TREE LOGIC ---
document.getElementById('deleteTreeButton').onclick = async function() {
    // 1. Get the ID from the input field in this section
    const container = this.closest('.sub-menu');
    const treeId = container.querySelector('#idFilter').value;

    if (!treeId) {
        alert("Please enter a Tree ID to delete.");
        return;
    }

    // 2. Confirmation Dialog to prevent accidental deletions
    const confirmDelete = confirm(`Are you sure you want to permanently delete Tree ${treeId}? This action cannot be undone.`);
    
    if (!confirmDelete) return;

    try {
        // 3. Send the DELETE request to your Flask API
        const response = await fetch(`${API_BASE_URL}/tree/${treeId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message);

            // 4. Update the UI: Remove the tree from the map
            // Refresh the whole layer
            loadAllTrees();

            // 5. Clear the input field
            container.querySelector('#idFilter').value = '';
            
            // Zoom back out to show the whole grid
            map.flyTo([38.7448, -9.1607], 12.5);
        } else {
            alert("Error: " + (result.error || "Failed to delete the tree."));
        }
    } catch (error) {
        console.error("Delete Error:", error);
        alert("Could not connect to the server.");
    }
};

// -- 3.7. ADD MAINTENANCE RECORD LOGIC ---
document.getElementById('addMaintButton').onclick = async function() {
    // 1. Scope to the specific "Add Maintenance" sub-menu
    const container = this.closest('.sub-menu');

    // 2. Gather values from the inputs
    const treeId = container.querySelector('#idFilter').value;
    const payload = {
        op_code: container.querySelector('#opcodes').value,
        maint_date: container.querySelector('#date').value,
        observation: container.querySelector('#observe').value,
        officer: container.querySelector('#officer').value
    };

    // 3. Basic Validation
    if (!treeId || !payload.op_code || !payload.maint_date) {
        alert("Please provide the Tree ID, Operation Code, and Date.");
        return;
    }

    try {
        // 4. Send POST request to the maintenance endpoint
        const response = await fetch(`${API_BASE_URL}/tree/${treeId}/maintenance`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message);
            
            // 5. Visual Feedback: Find the tree on the map to show where you added the log
            const detailRes = await fetch(`${API_BASE_URL}/tree/${treeId}`);
            const tree = await detailRes.json();
            
            if (!tree.error) {
                const geom = JSON.parse(tree.geometry);
                const lat = geom.coordinates[1];
                const lon = geom.coordinates[0];

                // Fly to the tree and open a popup confirming the maintenance
                map.flyTo([lat, lon], 18);
                L.popup()
                    .setLatLng([lat, lon])
                    .setContent(`
                        <div style="font-family: sans-serif;">
                            <h4 style="margin:0; color:#2980b9;">Maintenance Logged</h4>
                            <hr>
                            <b>Tree ID:</b> ${treeId}<br>
                            <b>Op Code:</b> ${payload.op_code}<br>
                            <b>Officer:</b> ${payload.officer}
                        </div>
                    `)
                    .openOn(map);
            }

            // 6. Clear the form
            container.querySelectorAll('input').forEach(input => input.value = '');
        } else {
            alert("Error: " + (result.error || "Failed to add maintenance record."));
        }
    } catch (error) {
        console.error("Maintenance Error:", error);
        alert("Could not connect to the server.");
    }
};

// -- 3.8. VIEW MAINTENANCE LOGIC --
document.getElementById('viewMaintButton').onclick = async function() {
    const container = this.closest('.sub-menu');
    const treeId = container.querySelector('#idFilter').value;
    const limit = container.querySelector('#limit').value || 5;

    if (!treeId) {
        alert("Please enter a Tree ID to view history.");
        return;
    }

    try {
        // 1. Fetch maintenance history
        const response = await fetch(`${API_BASE_URL}/tree/${treeId}/maintenance?limit=${limit}`);
        const history = await response.json();

        // 2. Fetch tree location for zooming
        const treeRes = await fetch(`${API_BASE_URL}/tree/${treeId}`);
        const treeData = await treeRes.json();

        if (treeData.error) {
            alert("Tree not found.");
            return;
        }

        // --- CLEAR ALL TREES FROM THE MAP ---
        treeLayer.clearLayers();

        // 3. Process coordinates and add ONLY this tree back to the map
        const geom = JSON.parse(treeData.geometry);
        const lat = geom.coordinates[1];
        const lon = geom.coordinates[0];

        // Add a highlighted marker for this specific tree
        const highlightedMarker = L.circleMarker([lat, lon], {
            radius: 10,
            fillColor: "#2d5a27",
            color: "#fff",
            weight: 2,
            fillOpacity: 1
        }).addTo(treeLayer);

        // highlightedMarker.bindPopup(`
        //     <b>Tree ID: ${treeId}</b><br>
        // `).openPopup();

        // Zoom to the point
        map.flyTo([lat, lon], 17);

        // 4. Render logs in the bottom-left panel
        const panel = document.getElementById('maintenanceResultsPanel');
        const content = document.getElementById('maintContent');
        
        panel.style.display = 'block';
        
        if (history.length === 0) {
            content.innerHTML = "<p>No maintenance records found for this tree.</p>";
        } else {
            content.innerHTML = history.map(log => `
                <div class="maint-card">
                    <small style="color: #27ae60;">${new Date(log.maint_date).toLocaleDateString()}</small><br>
                    <b>Action:</b> ${log.op_description}<br>
                    <b>Officer:</b> ${log.officer}<br>
                    <p style="margin: 5px 0; font-style: italic;">"${log.observation || 'No comments'}"</p>
                </div>
            `).join('');
        }

    } catch (error) {
        console.error("View Maintenance Error:", error);
        alert("Could not retrieve history.");
    }
};


// -- 3.9. ADD COMMENT LOGIC --
document.getElementById('addCommentButton').onclick = async function() {
    // 1. Scope to the "Add Comment" sub-menu
    const container = this.closest('.sub-menu');

    // 2. Gather values from the inputs
    const treeId = container.querySelector('#idFilter').value;
    const payload = {
        username: container.querySelector('#user').value.trim(),
        comment: container.querySelector('#comment').value.trim()
    };

    // 3. Validation
    if (!treeId || !payload.username || !payload.comment) {
        alert("Please provide a Tree ID, Username, and a Comment.");
        return;
    }

    try {
        // 4. Send POST request to your Flask API
        const response = await fetch(`${API_BASE_URL}/tree/${treeId}/comment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message);
            
            // 5. Visual Feedback: Fly to the tree to show where the comment was pinned
            const detailRes = await fetch(`${API_BASE_URL}/tree/${treeId}`);
            const tree = await detailRes.json();
            
            if (!tree.error) {
                const geom = JSON.parse(tree.geometry);
                const lat = geom.coordinates[1];
                const lon = geom.coordinates[0];

                map.flyTo([lat, lon], 18);
                
                L.popup()
                    .setLatLng([lat, lon])
                    .setContent(`
                        <div style="font-family: sans-serif; max-width: 200px;">
                            <h4 style="margin:0; color:#8e44ad;">New Comment Added</h4>
                            <hr>
                            <b>User:</b> ${payload.username}<br>
                            <b>Comment:</b> "${payload.comment}"
                        </div>
                    `)
                    .openOn(map);
            }

            // 6. Clear form fields
            container.querySelectorAll('input').forEach(input => input.value = '');
        } else {
            alert("Error: " + (result.error || "Failed to submit comment."));
        }
    } catch (error) {
        console.error("Comment Submission Error:", error);
        alert("Could not connect to the server.");
    }
};

// -- 3.10. VIEW COMMENTS LOGIC --
document.getElementById('viewCommentButton').onclick = async function() {
    const container = this.closest('.sub-menu');
    const treeId = container.querySelector('#idFilter').value;
    const limit = container.querySelector('#limit').value || 10;

    if (!treeId) {
        alert("Please enter a Tree ID to view comments.");
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/tree/${treeId}/comments?limit=${limit}`);
        const comments = await response.json();

        const treeRes = await fetch(`${API_BASE_URL}/tree/${treeId}`);
        const treeData = await treeRes.json();

        if (treeData.error) {
            alert("Tree not found.");
            return;
        }

        // Clear and Highlight
        treeLayer.clearLayers();
        const geom = JSON.parse(treeData.geometry);
        const latLng = [geom.coordinates[1], geom.coordinates[0]];

        L.circleMarker(latLng, {
            radius: 10,
            fillColor: "#9b59b6", 
            color: "#fff",
            weight: 2,
            fillOpacity: 1
        }).addTo(treeLayer);

        map.flyTo(latLng, 18);

        // Render to the correct panel
        const panel = document.getElementById('commentResultsPanel');
        const content = document.getElementById('commentContent');
        
        panel.style.display = 'block';
        
        if (comments.length === 0) {
            content.innerHTML = "<p>No comments found for this tree.</p>";
        } else {
            content.innerHTML = comments.map(c => `
                <div class="comment-card">
                    <b style="color: #9b59b6;">@${c.username}</b> 
                    <small style="float: right; color: #888;">${new Date(c.created_at).toLocaleDateString()}</small>
                    <p style="margin: 5px 0;">${c.comment}</p>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error("View Comment Error:", error);
        alert("Failed to retrieve comments.");
    }
};

