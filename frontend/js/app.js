const API_URL = "https://recyclex-backend.onrender.com";

function showAlert(message, type="success") {
    const box = document.getElementById("alertBox");
    if (!box) return;
    box.textContent = message;
    box.className = `alert ${type}`;
    box.style.display = "block";
    
    setTimeout(() => {
        box.style.display = "none";
    }, 5000);
}

function toggleSidebar() {
    const sb = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");
    if(sb) sb.classList.toggle("open");
    if(overlay) overlay.classList.toggle("active");
}

function toggleCreditDropdown() {
    const dropdown = document.getElementById("creditDropdown");
    if (dropdown) {
        dropdown.style.display = dropdown.style.display === "none" ? "flex" : "none";
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById("creditDropdown");
    if (dropdown && dropdown.style.display === "flex") {
        const button = event.target.closest('button[onclick="toggleCreditDropdown()"]');
        if (!button && !dropdown.contains(event.target)) {
            dropdown.style.display = "none";
        }
    }
});

// OTP functionality removed as requested.

async function submitRegister() {
    const payload = {
        name: document.getElementById("regName").value,
        email: document.getElementById("regEmail").value,
        password: document.getElementById("regPassword").value,
        phone: document.getElementById("regPhone").value,
        address: document.getElementById("regAddress").value,
        city: document.getElementById("regCity").value,
        state: document.getElementById("regState").value,
        pincode: document.getElementById("regPincode").value,
        role: document.getElementById("regRole").value,
        landmark: document.getElementById("regLandmark") ? document.getElementById("regLandmark").value : "",
        live_location: document.getElementById("regLiveLocation") ? document.getElementById("regLiveLocation").value : ""
    };

    try {
        const res = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        if (res.ok) {
            showAlert("Registration Successful! Redirecting to login...", "success");
            setTimeout(() => {
                window.location.href = "login.html";
            }, 1500);
        } else {
            showAlert(data.detail || "Registration failed", "error");
        }
    } catch (err) {
        showAlert("Server connection failed", "error");
    }
}

async function submitLogin() {
    const payload = {
        email: document.getElementById("logEmail").value,
        password: document.getElementById("logPassword").value
    };

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        if (res.ok) {
            // Store user session in localStorage
            localStorage.setItem("recyclex_user", JSON.stringify(data.user));
            showAlert("Login Successful! Processing...", "success");
            
            setTimeout(() => {
                if (data.user.role === "admin") {
                    window.location.href = "dashboard_admin.html";
                } else {
                    window.location.href = "dashboard_user.html";
                }
            }, 1000);
        } else {
            showAlert(data.detail || "Invalid Credentials", "error");
        }
    } catch (err) {
        showAlert("Server connection failed", "error");
    }
}

// Ensure the user is logged in for protected pages
function requireAuth(expectedRole = null) {
    const userJson = localStorage.getItem("recyclex_user");
    if (!userJson) {
        window.location.href = "login.html";
        return null;
    }
    
    const user = JSON.parse(userJson);
    if (expectedRole && user.role !== expectedRole) {
        window.location.href = "login.html";
        return null;
    }
    
    return user;
}

function logout() {
    localStorage.removeItem("recyclex_user");
    window.location.href = "login.html";
}

async function refreshStats() {
    const user = requireAuth('user');
    if (!user) return;
    
    try {
        const res = await fetch(`${API_URL}/users/${user.id}`);
        const data = await res.json();
        if (res.ok) {
            document.getElementById("ecoPoints").textContent = data.eco_points;
            document.getElementById("co2Saved").textContent = data.co2_saved.toFixed(2) + " kg";
            if(document.getElementById("userCredits")) {
                document.getElementById("userCredits").textContent = "₹" + (data.credits || 0).toFixed(2);
            }
            
            // Gamified Reward Logic
            const rewardPanel = document.getElementById("gamifiedRewardPanel");
            if (rewardPanel && data.has_guardian_badge) {
                rewardPanel.style.display = "block";
            }
        }
    } catch (e) {
        console.error("Failed to fetch user stats", e);
    }
}

async function convertPoints() {
    const user = requireAuth('user');
    if (!user) return;
    
    if (!confirm("Are you sure you want to convert 100 Eco Points into 1 Credit?")) return;
    
    try {
        const res = await fetch(`${API_URL}/users/${user.id}/convert-points`, {
            method: 'POST'
        });
        const data = await res.json();
        
        if (res.ok) {
            showAlert(data.message, "success");
            refreshStats(); // Update UI
        } else {
            showAlert(data.detail || "Conversion failed. You need at least 100 Eco Points.", "error");
        }
    } catch (e) {
        showAlert("Server connection failed", "error");
    }
}

async function submitScrap() {
    const user = requireAuth('user');
    if (!user) return;
    
    const fileInput = document.getElementById("scrapFile");
    if (!fileInput.files[0]) {
        showAlert("Please select an image first", "error");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    
    try {
        const res = await fetch(`${API_URL}/upload_scrap?seller_id=${user.id}`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        
        if (res.ok) {
            document.getElementById("scanResult").style.display = "block";
            document.getElementById("detectedType").textContent = data.type;
            document.getElementById("scanMessage").textContent = data.message;
            
            showAlert("Image classified successfully!", "success");
            refreshStats(); // Update eco points
        } else {
            showAlert("Upload failed", "error");
        }
    } catch (err) {
        showAlert("Server connection failed", "error");
    }
}

async function fetchMarketplace() {
    try {
        const res = await fetch(`${API_URL}/marketplace`);
        const data = await res.json();
        
        const container = document.getElementById("marketplaceList");
        container.innerHTML = "";
        
        if (data.length === 0) {
            container.innerHTML = '<p style="color: var(--text-muted);">No scrap available right now.</p>';
            return;
        }
        
        data.forEach(item => {
            const div = document.createElement("div");
            div.className = "marketplace-card animate-in";
            div.innerHTML = `
                <div style="display: flex; align-items: center; width: 100%;">
                    <div class="scrap-preview-wrapper" style="margin-right: 1.5rem;">
                        <img src="${API_URL}/${item.image}" alt="Scrap component" onerror="this.src='https://via.placeholder.com/120?text=No+Image'">
                    </div>
                    <div style="flex-grow: 1;">
                        <h4 style="color: var(--primary-green); font-size: 1.25rem; font-weight: 700;">${item.type}</h4>
                        <p style="font-size: 0.9rem; color: var(--text-main); margin-top: 0.25rem;"><i class="fa-solid fa-location-dot"></i> ${item.address}, ${item.city}</p>
                        <p style="font-size: 0.85rem; color: #f59e0b; margin-top: 0.25rem; font-weight: 600;">Status: ${item.status.toUpperCase()}</p>
                    </div>
                    <div>
                        ${item.status === 'available' ? 
                          `<button class="btn btn-secondary" style="white-space: nowrap;" onclick="bookMarketplaceItem(${item.id})">Provide Quote</button>` : 
                          `<span style="color: var(--text-muted); font-size: 0.85rem; background: rgba(0,0,0,0.05); padding: 0.5rem 1rem; border-radius: 20px;">Quote Pending User</span>`
                        }
                    </div>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (e) {
        console.error(e);
    }
}

async function fetchOptimizedRoutes() {
    try {
        const res = await fetch(`${API_URL}/routes`);
        const data = await res.json();
        
        const container = document.getElementById("routeList");
        container.innerHTML = "";
        
        if (data.length === 0) {
            container.innerHTML = '<p style="color: var(--text-muted);">No pickups active to route.</p>';
            return;
        }
        
        container.className = "route-timeline";
        
        data.forEach((route, index) => {
            const div = document.createElement("div");
            div.className = `route-node animate-in ${route.status.toLowerCase() === 'pending' ? 'pending' : ''}`;
            div.style.animationDelay = `${index * 0.1}s`;
            // Demonstrating scikit-learn cluster mapping
            div.innerHTML = `
                <div>
                    <h4 style="color: var(--primary-green); margin-bottom: 0.5rem; font-size: 1.1rem;">#${index + 1} - ${route.scrap_type} Pickup</h4>
                    <p style="font-size: 0.9rem; color: var(--text-main);"><i class="fa-solid fa-location-dot" style="color: #f59e0b; margin-right: 0.5rem;"></i>${route.address}</p>
                    <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;"><i class="fa-solid fa-route" style="margin-right:0.25rem;"></i> Cluster: ${route.cluster ?? 0} | Coordinates: [${route.lat.toFixed(5)}, ${route.lon.toFixed(5)}] | Status: <span style="font-weight: 600; color: ${route.status.toLowerCase() === 'pending' ? '#f59e0b' : 'var(--primary-green)'};">${route.status}</span></p>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (e) {
        console.error(e);
    }
}

async function bookMarketplaceItem(scrapId) {
    const user = requireAuth('admin');
    if (!user) return;
    
    const bidAmount = prompt("Enter your quote amount (₹) for this scrap:");
    if (!bidAmount || isNaN(bidAmount)) {
        showAlert("Invalid bid amount", "error");
        return;
    }
    
    try {
        const res = await fetch(`${API_URL}/marketplace/bid`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scrap_id: scrapId, amount: parseFloat(bidAmount), admin_id: user.id })
        });
        const data = await res.json();
        
        if (res.ok) {
            showAlert(`Quote submitted successfully! Waiting for user approval.`, "success");
            fetchMarketplace(); // refresh list
        } else {
            showAlert("Failed to place bid", "error");
        }
    } catch (e) {
        showAlert("Server connection failed", "error");
    }
}

async function fetchPendingBids() {
    const user = requireAuth('user');
    if (!user) return;
    
    try {
        const res = await fetch(`${API_URL}/users/${user.id}/history`);
        const data = await res.json();
        
        const biddedItems = data.filter(item => item.status === 'bidded');
        const container = document.getElementById("pendingBidsList");
        if (!container) return; // Might not exist if on wrong page
        
        container.innerHTML = "";
        
        if (biddedItems.length === 0) {
            container.innerHTML = '<p style="color: var(--text-muted);">No pending bids awaiting your approval.</p>';
            return;
        }
        
        biddedItems.forEach(item => {
            const div = document.createElement("div");
            div.className = "marketplace-card animate-in";
            div.style.background = "rgba(16, 185, 129, 0.05)";
            div.innerHTML = `
                <div style="flex: 1;">
                    <h4 style="color: var(--text-main); font-weight: 700;">${item.type}</h4>
                    <p style="font-size: 0.85rem; color: #f59e0b; margin-top: 0.25rem; font-weight: 600;">Offered Price: ₹${item.price}</p>
                    <p style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.2rem;">Decline if you want a higher offer — admin can rebid.</p>
                </div>
                <div style="display: flex; gap: 0.5rem; flex-shrink: 0;">
                    <button class="btn" style="padding: 0.5rem 1rem;" onclick="approveBid(${item.id})">
                        <i class="fa-solid fa-circle-check" style="margin-right:0.35rem;"></i>Accept
                    </button>
                    <button onclick="declineBid(${item.id})" style="padding: 0.5rem 1rem; background: rgba(239,68,68,0.1); color: #ef4444; border: 1.5px solid rgba(239,68,68,0.4); border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.9rem; display:flex; align-items:center; gap:0.35rem;">
                        <i class="fa-solid fa-circle-xmark"></i>Decline
                    </button>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (e) {
        console.error(e);
    }
}

async function approveBid(scrapId) {
    try {
        const res = await fetch(`${API_URL}/marketplace/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scrap_id: scrapId })
        });
        const data = await res.json();
        
        if (res.ok) {
            showAlert(data.message, "success");
            fetchPendingBids();
            refreshStats(); // CO2 saved should increase
        } else {
            showAlert("Failed to approve", "error");
        }
    } catch (e) {
        showAlert("Server connection failed", "error");
    }
}

async function declineBid(scrapId) {
    if (!confirm("Decline this offer? The admin will be able to submit a new, higher quote.")) return;
    try {
        const res = await fetch(`${API_URL}/marketplace/decline`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scrap_id: scrapId })
        });
        const data = await res.json();
        
        if (res.ok) {
            showAlert("Offer declined. Admin can now submit a higher quote.", "success");
            fetchPendingBids();
        } else {
            showAlert("Failed to decline offer", "error");
        }
    } catch (e) {
        showAlert("Server connection failed", "error");
    }
}

async function showUserHistory() {
    const user = requireAuth('user');
    if (!user) return;

    try {
        const res = await fetch(`${API_URL}/users/${user.id}/history`);
        const data = await res.json();
        
        const modal = document.getElementById('historyModal');
        const list = document.getElementById('historyList');
        
        if (res.ok) {
            modal.style.display = "flex";
            if (data.length === 0) {
                list.innerHTML = "<p style='color: var(--text-muted);'>No scrap history found.</p>";
            } else {
                list.innerHTML = data.map(item => `
                    <div style="background: var(--surface-card, rgba(16,185,129,0.05)); padding: 1rem; border-radius: 4px; margin-bottom: 0.5rem; border-left: 4px solid var(--primary-green);">
                        <div style="display: flex; justify-content: space-between;">
                            <strong style="color: var(--text-main);">${item.type}</strong>
                            <span style="color: ${item.status === 'sold' ? 'var(--primary-green)' : '#f59e0b'};">${(item.pickup_status || item.status).toUpperCase()}</span>
                        </div>
                        <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">Price/Reward: ${item.price ? '₹'+item.price : 'Pending'}</p>
                        ${item.status === 'sold' && item.admin_name ? 
                            `<div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid var(--border-light);">
                                <p style="font-size: 0.8rem; color: #3b82f6;"><strong>Collector:</strong> ${item.admin_name} (Ph: ${item.admin_phone}) is on the way.</p>
                             </div>` : ''}
                    </div>
                `).join('');
            }
        } else {
            showAlert("Could not load history", "error");
        }
    } catch (e) {
        showAlert("Server offline or unavailable", "error");
    }
}

async function showAdminHistory() {
    const user = requireAuth('admin');
    if (!user) return;

    try {
        const res = await fetch(`${API_URL}/admin/history`);
        const data = await res.json();
        
        const modal = document.getElementById('historyModal');
        const list = document.getElementById('historyList');
        
        if (res.ok) {
            modal.style.display = "flex";
            document.getElementById('adminTotalOrders').textContent = data.orders_taken_today;
            document.getElementById('adminTotalSpent').textContent = "₹" + data.total_spent.toFixed(2);

            if (data.recent_pickups.length === 0) {
                list.innerHTML = "<p style='color: var(--text-muted);'>No scrap purchases recorded yet.</p>";
            } else {
                list.innerHTML = data.recent_pickups.map(item => `
                    <div style="background: var(--surface-card, rgba(16,185,129,0.05)); padding: 1rem; border-radius: 4px; margin-bottom: 0.5rem; border-left: 4px solid var(--primary-green);">
                        <div style="display: flex; justify-content: space-between;">
                            <strong style="color: var(--text-main);">${item.scrap_type} Pickup</strong>
                            <span style="color: var(--primary-green);">${item.status.toUpperCase()}</span>
                        </div>
                        <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">Location: ${item.address}</p>
                    </div>
                `).join('');
            }
        } else {
            showAlert("Could not load history", "error");
        }
    } catch (e) {
        showAlert("Server offline or unavailable", "error");
    }
}

const translations = {
    en: {
        dashboard: "Dashboard",
        home: "Home",
        logout: "Logout",
        history: "History",
        pending_quotes: "Pending Scrap Offers"
    },
    hi: {
        dashboard: "डैशबोर्ड",
        home: "होम",
        logout: "लॉग आउट",
        history: "इतिहास",
        pending_quotes: "लंबित कबाड़ ऑफ़र"
    },
    mr: {
        dashboard: "डॅशबोर्ड",
        home: "मुख्यपृष्ठ",
        logout: "लॉगआउट",
        history: "इतिहास",
        pending_quotes: "प्रलंबित भंगार ऑफर"
    }
};

function changeLanguage(lang) {
    if(!translations[lang]) return;
    const t = translations[lang];
    document.querySelectorAll('.nav-links a').forEach(el => {
        const text = el.textContent.trim().toLowerCase();
        if (text === 'home' || text === 'होम' || text === 'मुख्यपृष्ठ') el.textContent = t.home;
        if (text === 'dashboard' || text === 'डैशबोर्ड' || text === 'डॅशबोर्ड') el.textContent = t.dashboard;
        if (text === 'history' || text === 'इतिहास') el.textContent = t.history;
    });
    const logoutBtn = document.querySelector('.nav-links button');
    if (logoutBtn) logoutBtn.textContent = t.logout;
    
    document.querySelectorAll('h2').forEach(h2 => {
        if (h2.textContent.includes('Pending') || h2.textContent.includes('लंबित') || h2.textContent.includes('प्रलंबित')) {
            h2.textContent = t.pending_quotes;
        }
    });
    localStorage.setItem('recyclex_lang', lang);
}

// Theme toggle logic
function toggleTheme() {
    const root = document.documentElement;
    const currentTheme = root.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    root.setAttribute('data-theme', newTheme);
    localStorage.setItem('recyclex_theme', newTheme);
    
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icons = document.querySelectorAll('.theme-icon');
    icons.forEach(icon => {
        if (theme === 'dark') {
            icon.className = "fa-solid fa-sun theme-icon";
        } else {
            icon.className = "fa-solid fa-moon theme-icon";
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('recyclex_lang');
    if (saved) {
        const switcher = document.getElementById('languageSwitcher');
        if (switcher) switcher.value = saved;
        setTimeout(() => changeLanguage(saved), 100);
    }
    
    const savedTheme = localStorage.getItem('recyclex_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    // Use a small timeout to let the DOM settle if elements are dynamically added
    setTimeout(() => updateThemeIcon(savedTheme), 50);
});