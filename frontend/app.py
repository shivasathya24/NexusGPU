import streamlit as st
import requests
import os
import time

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="GPU Nexus AIOps",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Backend URL config
def get_backend_url():
    keys = ["BACKEND_URL", "backend_url", "BackendUrl", "Backend_URL"]
    url = None
    for key in keys:
        try:
            if key in st.secrets:
                url = st.secrets[key]
                break
        except Exception:
            pass
    if not url:
        for key in keys:
            val = os.getenv(key)
            if val:
                url = val
                break
    if not url:
        url = "http://127.0.0.1:8000"
    
    # Strip spaces and trailing slashes
    url = url.strip().rstrip("/")
    
    # Ensure scheme is present (e.g. add https:// if missing)
    if not url.startswith("http://") and not url.startswith("https://"):
        if "127.0.0.1" in url or "localhost" in url:
            url = "http://" + url
        else:
            url = "https://" + url
    return url

BACKEND_URL = get_backend_url()

def load_css(file_name):
    # Try to load custom styles
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        # Fallback if file not found during local debugging
        pass

# Load the custom styles
load_css("frontend/assets/styles.css")
load_css("assets/styles.css")  # Double fallback depending on working directory

# Session State navigation
if "page" not in st.session_state:
    st.session_state.page = "Landing Page"

# Verify API availability
api_online = False
try:
    response = requests.get(f"{BACKEND_URL}/", timeout=5.0)
    if response.status_code == 200:
        api_online = True
except Exception:
    pass

# Import page renderers
from pages.landing import render_landing
from pages.dashboard import render_dashboard
from pages.analytics import render_analytics
from pages.assistant import render_assistant
from pages.settings import render_settings

# Header / Navigation Panel (Horizontal)
col_logo, col_opt1, col_opt2, col_opt3, col_opt4, col_opt5 = st.columns([2.2, 1.0, 1.2, 1.0, 1.2, 1.0])

with col_logo:
    status_class = "status-healthy" if api_online else "status-critical"
    status_label = "ONLINE" if api_online else f"OFFLINE ({BACKEND_URL.replace('https://', '')})"
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-top: 5px;">
            <h2 style="color: #00E5FF; margin: 0; font-family: 'Outfit', sans-serif; font-size: 24px; text-shadow: 0 0 15px rgba(0,229,255,0.4);">⚡ GPU NEXUS</h2>
            <span class="status-pill {status_class}" style="padding: 2px 8px !important; font-size: 9px !important; white-space: nowrap;">
                <span class="status-pulse"></span>
                {status_label}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

menu_options = [
    {"name": "Landing Page", "icon": "🚀", "label": "Home", "col": col_opt1},
    {"name": "Main Dashboard", "icon": "📊", "label": "Dashboard", "col": col_opt2},
    {"name": "Analytics & Reports", "icon": "📈", "label": "Analytics", "col": col_opt3},
    {"name": "Nexus AI Assistant", "icon": "🧠", "label": "AI Assistant", "col": col_opt4},
    {"name": "Cluster Settings", "icon": "⚙️", "label": "Settings", "col": col_opt5}
]

for option in menu_options:
    with option["col"]:
        label = f"{option['icon']}  {option['label']}"
        if st.session_state.page == option['name']:
            st.button(label, key=f"btn_{option['name']}", use_container_width=True, type="primary")
        else:
            if st.button(label, key=f"btn_{option['name']}", use_container_width=True):
                st.session_state.page = option['name']
                st.rerun()

st.markdown("<hr style='border-color: rgba(255,255,255,0.06); margin-top: 15px; margin-bottom: 25px;'>", unsafe_allow_html=True)

# Render Pages
if st.session_state.page == "Landing Page":
    render_landing()
elif st.session_state.page == "Main Dashboard":
    render_dashboard(api_online)
elif st.session_state.page == "Analytics & Reports":
    render_analytics(api_online)
elif st.session_state.page == "Nexus AI Assistant":
    render_assistant(api_online)
elif st.session_state.page == "Cluster Settings":
    render_settings(api_online)

# Inject Real-time Draggable Power Telemetry Widget HTML
st.markdown(
    """
    <div id="floating-power-widget" class="floating-power-widget">
        <div id="floating-widget-header">
            <span style="font-weight: 700; color: #00E5FF; font-size: 11px; display: flex; align-items: center; gap: 4px;">
                <span class="status-pulse" style="background-color: #00E5FF; width: 6px; height: 6px; box-shadow: 0 0 8px #00E5FF;"></span>
                LIVE POWER STREAM
            </span>
            <div style="display: flex; gap: 8px; align-items: center;">
                <span id="pip-btn" style="font-size: 9px; color: #00E5FF; cursor: pointer; font-weight: bold; user-select: none; background: rgba(0, 229, 255, 0.1); padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(0, 229, 255, 0.3);" title="Float widget on top of other desktop apps (Always on top)">📌 PIN</span>
                <span id="widget-drag-label" style="font-size: 9px; color: #64748B; cursor: move; font-weight: bold; user-select: none;">[DRAG]</span>
            </div>
        </div>
        <div class="floating-metric-row">
            <span class="floating-label">Cluster Total:</span>
            <span id="float-total-power" class="floating-value text-nvidia">1,820 W</span>
        </div>
        <div class="floating-metric-row">
            <span class="floating-label">Grid State:</span>
            <span id="float-grid-state" class="floating-value" style="color: #10B981;">OFF-PEAK</span>
        </div>
        <div class="floating-metric-row">
            <span class="floating-label">Savings:</span>
            <span id="float-savings" class="floating-value" style="color: #A855F7;">$6.00 USD</span>
        </div>
        <div class="floating-metric-row">
            <span class="floating-label">Efficiency:</span>
            <span id="float-efficiency" class="floating-value" style="color: #F59E0B;">89.0%</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Inject parent script via Streamlit Component iframe (appends a script tag to the top-level window body)
import streamlit.components.v1 as components
components.html(
    """
    <script>
        (function() {
            var parentDoc = window.parent.document;
            
            // Check if already injected in the parent. If so, just call the init function to re-bind elements.
            if (window.parent.nexusInitWidget) {
                window.parent.nexusInitWidget();
                return;
            }
            
            var script = parentDoc.createElement("script");
            script.textContent = `
                (function() {
                    function initWidget() {
                        var el = document.getElementById("floating-power-widget");
                        var existing = document.getElementById("floating-power-widget-body");
                        
                        if (!el && !existing) {
                            setTimeout(initWidget, 100);
                            return;
                        }
                        
                        if (existing) {
                            if (window.nexusWidgetX !== undefined) {
                                el.style.transform = "translate3d(" + window.nexusWidgetX + "px, " + window.nexusWidgetY + "px, 0)";
                            }
                            existing.remove();
                        }
                        
                        if (el) {
                            el.id = "floating-power-widget-body";
                            document.body.appendChild(el);
                            setupDragging(el);
                            setupPiP(el);
                        }
                        
                        setupTelemetry();
                    }
                    
                    window.nexusInitWidget = initWidget;
                    
                    function setupDragging(element) {
                        var header = document.getElementById("floating-widget-header");
                        if (!header) return;
                        
                        var isDragging = false;
                        var currentX = window.nexusWidgetX || 0;
                        var currentY = window.nexusWidgetY || 0;
                        var initialX;
                        var initialY;
                        var xOffset = currentX;
                        var yOffset = currentY;
                        
                        if (xOffset !== 0 || yOffset !== 0) {
                            element.style.transform = "translate3d(" + xOffset + "px, " + yOffset + "px, 0)";
                        }
                        
                        header.addEventListener("mousedown", dragStart, false);
                        document.addEventListener("mouseup", dragEnd, false);
                        document.addEventListener("mousemove", drag, false);
                        
                        function dragStart(e) {
                            initialX = e.clientX - xOffset;
                            initialY = e.clientY - yOffset;
                            if (e.target === header || header.contains(e.target)) {
                                isDragging = true;
                            }
                        }
                        
                        function dragEnd(e) {
                            initialX = currentX;
                            initialY = currentY;
                            isDragging = false;
                            window.nexusWidgetX = xOffset;
                            window.nexusWidgetY = yOffset;
                        }
                        
                        function drag(e) {
                            if (isDragging) {
                                e.preventDefault();
                                currentX = e.clientX - initialX;
                                currentY = e.clientY - initialY;
                                xOffset = currentX;
                                yOffset = currentY;
                                element.style.transform = "translate3d(" + currentX + "px, " + currentY + "px, 0)";
                            }
                        }
                    }
                    
                    function setupPiP(element) {
                        var pipBtn = document.getElementById("pip-btn");
                        if (!pipBtn) return;
                        
                        pipBtn.addEventListener("click", async function() {
                            if (!window.documentPictureInPicture) {
                                alert("Your browser does not support Document Picture-in-Picture. Please use Chrome 116+ or Edge to float the widget!");
                                return;
                            }
                            
                            if (window.pipWindow) {
                                window.pipWindow.close();
                                return;
                            }
                            
                            try {
                                const pipWindow = await window.documentPictureInPicture.requestWindow({
                                    width: 280,
                                    height: 200
                                });
                                
                                window.pipWindow = pipWindow;
                                
                                // Copy styling
                                var styles = Array.from(document.getElementsByTagName('style'));
                                var links = Array.from(document.getElementsByTagName('link'));
                                styles.concat(links).forEach(function(s) {
                                    if (s.tagName === 'STYLE' || s.rel === 'stylesheet') {
                                        pipWindow.document.head.appendChild(s.cloneNode(true));
                                    }
                                });
                                
                                pipWindow.document.body.style.background = "#05060f";
                                pipWindow.document.body.style.margin = "0";
                                pipWindow.document.body.style.padding = "10px";
                                pipWindow.document.body.style.overflow = "hidden";
                                pipWindow.document.body.style.display = "flex";
                                pipWindow.document.body.style.alignItems = "center";
                                pipWindow.document.body.style.justify = "center";
                                
                                element.style.position = "static";
                                element.style.transform = "none";
                                element.style.boxShadow = "none";
                                element.style.border = "none";
                                element.style.width = "100%";
                                element.style.height = "auto";
                                
                                var dragLabel = element.querySelector("#widget-drag-label");
                                if (dragLabel) dragLabel.style.display = "none";
                                
                                pipBtn.innerText = "🔌 RETURN";
                                pipBtn.style.color = "#FF3366";
                                pipBtn.style.borderColor = "rgba(255, 51, 102, 0.4)";
                                pipBtn.style.background = "rgba(255, 51, 102, 0.1)";
                                
                                pipWindow.document.body.appendChild(element);
                                
                                pipWindow.addEventListener("pagehide", () => {
                                    element.style.position = "fixed";
                                    element.style.bottom = "25px";
                                    element.style.right = "25px";
                                    element.style.width = "260px";
                                    element.style.border = "1px solid rgba(0, 229, 255, 0.25)";
                                    element.style.boxShadow = "0 10px 40px rgba(0, 0, 0, 0.6), 0 0 25px rgba(0, 229, 255, 0.15)";
                                    
                                    var x = window.nexusWidgetX || 0;
                                    var y = window.nexusWidgetY || 0;
                                    element.style.transform = "translate3d(" + x + "px, " + y + "px, 0)";
                                    
                                    if (dragLabel) dragLabel.style.display = "inline";
                                    
                                    pipBtn.innerText = "📌 PIN";
                                    pipBtn.style.color = "#00E5FF";
                                    pipBtn.style.borderColor = "rgba(0, 229, 255, 0.3)";
                                    pipBtn.style.background = "rgba(0, 229, 255, 0.1)";
                                    
                                    document.body.appendChild(element);
                                    window.pipWindow = null;
                                });
                                
                            } catch (err) {
                                console.error("Failed to open PiP window:", err);
                            }
                        });
                    }
                    
                    function setupTelemetry() {
                        if (window.nexusIntervalInitialized) {
                            return;
                        }
                        window.nexusIntervalInitialized = true;
                        
                        function updateMetrics() {
                            var activeEl = document.getElementById("floating-power-widget-body");
                            if (!activeEl && window.pipWindow) {
                                activeEl = window.pipWindow.document.getElementById("floating-power-widget-body");
                            }
                            
                            if (!activeEl) return;
                            
                            fetch("http://127.0.0.1:8000/api/power")
                                .then(r => r.json())
                                .then(data => {
                                    if (data) {
                                        var totalW = data.total_power_w || 1820;
                                        var isPeak = data.price_info ? data.price_info.is_peak_hour : false;
                                        var rate = data.price_info ? data.price_info.price_per_kwh : 0.12;
                                        var savedUsd = data.savings_info ? data.savings_info.saved_cost_usd : 6.00;
                                        
                                        var powerEl = activeEl.querySelector("#float-total-power");
                                        if (powerEl) powerEl.innerText = totalW.toFixed(0) + " W";
                                        
                                        var gridEl = activeEl.querySelector("#float-grid-state");
                                        if (gridEl) {
                                            gridEl.innerText = isPeak ? "PEAK ($" + rate + ")" : "OFF-PEAK ($" + rate + ")";
                                            gridEl.style.color = isPeak ? "#EF4444" : "#10B981";
                                        }
                                        
                                        var savingsEl = activeEl.querySelector("#float-savings");
                                        if (savingsEl) savingsEl.innerText = "$" + savedUsd.toFixed(2) + " USD";
                                    }
                                })
                                .catch(e => {
                                    // Simulated telemetry fallback when API is offline
                                    var totalW = 1800 + Math.random() * 40;
                                    var rate = 0.12;
                                    var savedUsd = 6.00 + (Date.now() % 60000) / 10000;
                                    
                                    var powerEl = activeEl.querySelector("#float-total-power");
                                    if (powerEl) powerEl.innerText = totalW.toFixed(0) + " W";
                                    
                                    var gridEl = activeEl.querySelector("#float-grid-state");
                                    if (gridEl) {
                                        gridEl.innerText = "OFF-PEAK ($" + rate + ")";
                                        gridEl.style.color = "#10B981";
                                    }
                                    
                                    var savingsEl = activeEl.querySelector("#float-savings");
                                    if (savingsEl) savingsEl.innerText = "$" + savedUsd.toFixed(2) + " USD";
                                });
                            
                            fetch("http://127.0.0.1:8000/api/batching")
                                .then(r => r.json())
                                .then(data => {
                                    if (data) {
                                        var eff = data.gpu_efficiency_score || 89.0;
                                        var effEl = activeEl.querySelector("#float-efficiency");
                                        if (effEl) effEl.innerText = eff.toFixed(1) + "%";
                                    }
                                })
                                .catch(e => {
                                    // Simulated telemetry fallback when API is offline
                                    var eff = 88.0 + Math.random() * 2;
                                    var effEl = activeEl.querySelector("#float-efficiency");
                                    if (effEl) effEl.innerText = eff.toFixed(1) + "%";
                                });
                        }
                        
                        setInterval(updateMetrics, 2000);
                        updateMetrics();
                    }
                    
                    initWidget();
                })();
            `;
            parentDoc.body.appendChild(script);
        })();
    </script>
    """.replace("http://127.0.0.1:8000", BACKEND_URL),
    height=0
)



