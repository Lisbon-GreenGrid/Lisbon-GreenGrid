
const API_BASE_URL = "http://localhost:5000";

// --- 1. MAP INITIALIZATION ---
var map = new L.Map('leaflet', {
    layers: [
        new L.TileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        })
    ],
    center: [38.7223, -9.1393], 
    zoom: 13
});
map.zoomControl.setPosition("bottomright");

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

// --- 3. CORE DATA LOADING ---
function loadAllTrees() {
    fetch(`${API_BASE_URL}/trees`)
        .then(res => res.json())
        .then(trees => {
            trees.forEach(tree => {
                const geom = JSON.parse(tree.geometry);
                const marker = L.circleMarker([geom.coordinates[1], geom.coordinates[0]], {
                    radius: 7, fillColor: "#2d5a27", color: "#fff", weight: 2, fillOpacity: 0.8
                }).addTo(map);
                marker.bindPopup(`<b>${tree.nome_vulga}</b><br>ID: ${tree.tree_id}<br>${tree.especie}`);
            });
        });
}
loadAllTrees();

// Helper for API Actions
async function apiAction(url, method, payload = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (payload) options.body = JSON.stringify(payload);
    
    try {
        const res = await fetch(url, options);
        const data = await res.json();
        alert(data.message || data.error || "Operation Successful");
        if (method !== 'GET') location.reload();
    } catch (e) {
        alert("Error: Could not connect to the API.");
    }
}

// --- 4. SEARCH DROPDOWN FIX ---
searchInput.addEventListener("input", function () {
    const query = searchInput.value.trim();
    let existingResults = document.getElementById("searchResultsDropdown");
    if (existingResults) existingResults.remove();
    
    if (query.length < 2) return;

    fetch(`${API_BASE_URL}/trees/species/${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
            const resultsDiv = document.createElement("div");
            resultsDiv.id = "searchResultsDropdown";
            
            data.forEach(tree => {
                const item = document.createElement("div");
                item.style.padding = "10px";
                item.style.cursor = "pointer";
                item.innerHTML = `<b>${tree.nome_vulga}</b> <small>(${tree.tree_id})</small>`;

                item.addEventListener("click", () => {
                    const geom = JSON.parse(tree.geometry);
                    map.setView([geom.coordinates[1], geom.coordinates[0]], 19);
                    resultsDiv.remove();
                    searchInput.value = tree.nome_vulga;
                });
                resultsDiv.appendChild(item);
            });
            document.querySelector(".search-box").appendChild(resultsDiv);
        });
});

// Close search dropdown if user clicks on map
map.on('click', () => {
    let drop = document.getElementById("searchResultsDropdown");
    if (drop) drop.remove();
});

// --- 5. SECTION HANDLERS ---

// FIND TREE BY ID
document.getElementById('findTreeButton').onclick = function() {
    const id = this.parentElement.querySelector('#idFilter').value;
    if(!id) return alert("Enter an ID");
    fetch(`${API_BASE_URL}/tree/${id}`).then(res => res.json()).then(tree => {
        if (tree.error) return alert("Tree not found");
        const geom = JSON.parse(tree.geometry);
        map.setView([geom.coordinates[1], geom.coordinates[0]], 19);
    });
};

// NEAREST TREE SEARCH
document.getElementById('nearTreeButton').onclick = function() {
    const lat = document.getElementById('latFilter').value;
    const lon = document.getElementById('lonFilter').value;
    const rad = document.getElementById('radiusFilter').value;
    if(!lat || !lon || !rad) return alert("Fill all fields");
    
    fetch(`${API_BASE_URL}/trees/near?lat=${lat}&lon=${lon}&radius=${rad}`)
        .then(res => res.json())
        .then(data => {
            L.circle([lat, lon], {radius: rad, color: 'var(--accent-colour)', fillOpacity: 0.1}).addTo(map);
            alert(`Found ${data.length} trees nearby.`);
        });
};

// CREATE TREE (Section 5)
document.getElementById('createButton').onclick = function() {
    const payload = {
        tree_id: document.getElementById('treeid').value,
        nome_vulga: document.getElementById('name').value,
        especie: document.getElementById('especie').value,
        tipologia: document.getElementById('tipologia').value,
        freguesia: document.getElementById('freg').value,
        lat: parseFloat(document.getElementById('lat').value),
        lon: parseFloat(document.getElementById('lon').value)
    };
    apiAction(`${API_BASE_URL}/tree`, 'POST', payload);
};

// UPDATE TREE (Section 6 - Uses Scope-Based Targeting)
document.getElementById('updateTreeButton').onclick = function() {
    const section = this.parentElement;
    const id = section.querySelector('#treeid').value;
    const payload = {
        nome_vulga: section.querySelector('#name').value,
        especie: section.querySelector('#especie').value,
        tipologia: section.querySelector('#tipologia').value,
        morada: section.querySelector('#morada').value,
        pap: section.querySelector('#pap').value,
        manutencao: section.querySelector('#manutencao').value
    };
    apiAction(`${API_BASE_URL}/tree/${id}`, 'PUT', payload);
};

// DELETE TREE
document.getElementById('deleteTreeButton').onclick = function() {
    const id = this.parentElement.querySelector('#idFilter').value;
    if(confirm(`Confirm deletion of tree ${id}?`)) {
        apiAction(`${API_BASE_URL}/tree/${id}`, 'DELETE');
    }
};

// ADD MAINTENANCE
document.getElementById('addMaintButton').onclick = function() {
    const id = this.parentElement.querySelector('#idFilter').value;
    const payload = {
        op_code: document.getElementById('opcodes').value,
        officer: document.getElementById('officer').value,
        maint_date: document.getElementById('date').value,
        observation: document.getElementById('observe').value
    };
    apiAction(`${API_BASE_URL}/tree/${id}/maintenance`, 'POST', payload);
};

// VIEW MAINTENANCE
document.getElementById('viewMaintButton').onclick = function() {
    const id = this.parentElement.querySelector('#idFilter').value;
    const limit = document.getElementById('limit').value || 10;
    const resultsArea = this.parentElement.querySelector('#results');
    
    fetch(`${API_BASE_URL}/tree/${id}/maintenance?limit=${limit}`)
        .then(res => res.json())
        .then(data => {
            resultsArea.innerHTML = data.length > 0 
                ? data.map(log => `<div class="comments"><b>${log.maint_date}</b>: ${log.op_description} (${log.officer})</div>`).join("")
                : "No logs found.";
        });
};

// ADD COMMENT
document.getElementById('addCommentButton').onclick = function() {
    const id = this.parentElement.querySelector('#idFilter').value;
    const payload = {
        username: document.getElementById('user').value,
        comment_text: document.getElementById('comment').value
    };
    apiAction(`${API_BASE_URL}/tree/${id}/comment`, 'POST', payload);
};

// VIEW COMMENTS
document.getElementById('viewCommentButton').onclick = function() {
    const id = this.parentElement.querySelector('#idFilter').value;
    const resultsArea = this.parentElement.querySelector('#results');
    
    fetch(`${API_BASE_URL}/tree/${id}/comments`)
        .then(res => res.json())
        .then(data => {
            resultsArea.innerHTML = data.length > 0 
                ? data.map(c => `<div class="comments"><b>${c.username}</b>: ${c.comment_text}</div>`).join("")
                : "No comments found.";
        });
};