import streamlit as st
import requests
import re

# ==============================================================================
# 1. CONFIGURATION AND STATE MANAGEMENT
# ==============================================================================

st.set_page_config(page_title="Rickipedia", page_icon="🧪", layout="wide")

BASE = "https://rickandmortyapi.com/api/"
TOTAL_CHARACTERS = 826  # Documented total

# Initialize session state variables for navigation, filtering, and theme
if 'page_view' not in st.session_state:
    st.session_state.page_view = 'Characters'
if 'selected_char_id' not in st.session_state:
    st.session_state.selected_char_id = None
if 'char_page' not in st.session_state:
    st.session_state.char_page = 1
if 'ep_page' not in st.session_state: 
    st.session_state.ep_page = 1
if 'loc_page' not in st.session_state: 
    st.session_state.loc_page = 1
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark' # Default theme

def toggle_theme():
    """Toggles between 'dark' and 'light' themes."""
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'


# ==============================================================================
# 2. API FUNCTIONS (Cached)
# ==============================================================================

@st.cache_data(ttl=300, show_spinner="Fetching data from the multiverse...", max_entries=50)
def api_get(endpoint: str, params: dict | None = None):
    """Generic cached GET to the Rick & Morty API."""
    url = BASE + endpoint
    r = requests.get(url, params=params, timeout=20)
    if r.status_code == 200:
        return r.json()
    # Bubble up structured error for display
    return {"error": f"API Error {r.status_code}: {r.text}"}

@st.cache_data(ttl=300, show_spinner=False)
def fetch_multiple(urls: list[str], limit: int = 8):
    """Fetch a set of related resources in one bulk API call."""
    ids = [extract_id_from_url(u) for u in urls if u]
    if not ids:
        return []
        
    ids_to_fetch = ids[:limit]
    
    # Determine endpoint (Episode or Character) based on the first URL
    endpoint = "character" if "character" in urls[0] else "episode"
    
    bulk_url = BASE + f"{endpoint}/{','.join(ids_to_fetch)}"
    
    try:
        r = requests.get(bulk_url, timeout=20)
        if r.status_code == 200:
            result = r.json()
            # API returns a dict for a single ID, list for multiple IDs
            return result if isinstance(result, list) else [result]
    except Exception as e:
        st.error(f"Error fetching bulk data: {e}")
        return []
    return []

# ==============================================================================
# 3. HELPER FUNCTIONS & CALLBACKS
# ==============================================================================

def status_class(s: str) -> str:
    """Returns CSS class name based on character status."""
    s = (s or "").lower()
    if s == "alive": return "alive"
    if s == "dead": return "dead"
    return "unknown"

def get_status_color(s: str) -> str:
    """Returns CSS variable for status color."""
    s = (s or "").lower()
    if s == "alive": return "var(--ok)"
    if s == "dead": return "var(--bad)"
    return "var(--warn)"

def extract_id_from_url(u: str) -> str:
    """Extracts the ID from a resource URL (e.g., .../episode/28 -> 28)."""
    try:
        match = re.search(r'/(\d+)/?$', u)
        return match.group(1) if match else ""
    except Exception:
        return ""

def set_detail_view(char_id):
    """Sets state to navigate to the Character Detail page."""
    st.session_state.selected_char_id = char_id
    st.session_state.page_view = 'Character_Detail'

def set_list_view():
    """Sets state to return from detail view to the Characters list."""
    st.session_state.selected_char_id = None
    st.session_state.page_view = 'Characters'

def reset_char_page():
    """Reresets the character page to 1 when a filter changes (search fix)."""
    st.session_state.char_page = 1

def pager_controls(info: dict, current_page_key: str, key_prefix: str = "pg"):
    """Renders pagination buttons and handles page change logic."""
    # Adjusted columns to ensure the buttons don't stretch excessively
    cols = st.columns([1, 2, 1])
    current_page = st.session_state[current_page_key]
    total_pages = info.get("pages", current_page)

    with cols[0]:
        # Previous button logic
        if st.button("← Prev", disabled=(current_page <= 1), key=f"{key_prefix}-prev"):
            st.session_state[current_page_key] = max(1, current_page - 1)
            st.rerun()

    with cols[1]:
        st.markdown(f"<p style='text-align:center; color:var(--text)'>**Page:** {current_page} of {total_pages} &bull; **Total Items:** {info.get('count','?')}</p>", unsafe_allow_html=True)

    with cols[2]:
        # Next button logic
        if st.button("Next →", disabled=(current_page >= total_pages), key=f"{key_prefix}-next"):
            st.session_state[current_page_key] = min(total_pages, current_page + 1)
            st.rerun()


def render_character_card(char: dict):
    """
    Renders a character card with a 'View Details' button below it.
    """
    char_id = char.get('id')
    status = char.get("status", "unknown")
    badge = status_class(status)
    img = char.get("image", "")
    title = char.get("name", "Unknown")
    species = char.get("species", "–")
    origin = (char.get("origin") or {}).get("name", "–")
    
    # Determine the status color for the View Details button (Issue 4)
    status_color = get_status_color(status)

    # 1. Render the visual card via Markdown (Added margin-bottom: 8px for spacing)
    st.markdown(f"""
    <div class="card" id="char-card-{char_id}" style="margin-bottom: 8px;">
      <div class="card-figure">
        <span class="badge {badge}">{status}</span>
        <img src="{img}" alt="{title}">
      </div>
      <div class="card-body">
        <div class="card-title">{title}</div>
        <div class="meta">Species: {species}</div>
        <div class="meta">Origin: {origin}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Render the explicit 'View Details' button
    # FIX: Use dynamic custom property to set button color on the wrapper (Issue 1)
    st.markdown(f"""
    <div style="--status-color-dyn: {status_color};">
    """, unsafe_allow_html=True)

    st.button(
        "View Details", 
        key=f"char_btn_{char_id}",
        on_click=set_detail_view,
        args=(char_id, ),
        use_container_width=True,
    )

    st.markdown("</div>", unsafe_allow_html=True) # Close the wrapper div


# ==============================================================================
# 4. VIEW RENDERING FUNCTIONS
# ==============================================================================

def render_character_detail_page(char_id: int):
    """Renders the full profile for a single character."""
    data = api_get(f"character/{char_id}")
    
    # FIX: Applying max-width class to control size of the "Back" button
    st.markdown('<div class="back-btn-wrapper">', unsafe_allow_html=True)
    if st.button(f"← Back to Characters"):
        set_list_view()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    if "error" in data:
        st.error(f"Could not load character details for ID {char_id}.")
        return

    char = data
    # FIX: The CSS below targets h1 in this context to reduce top margin (Issue 1)
    st.markdown(f"<h1 class='detail-title'>{char['name']}</h1>", unsafe_allow_html=True)
    
    # FIX: Status badge separated from title and aligned correctly (Issue 4)
    status_badge_html = f"<span class='badge {status_class(char.get('status'))}'>{char.get('status', 'Unknown')}</span>"
    st.markdown(f"<div class='status-container'><span class='status-label'>Status:</span> {status_badge_html}</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])
    with c1:
        # FIX: Removed the empty Streamlit element that caused the box/space above biographical details
        st.image(char['image'], use_container_width=True, caption=char['species'], output_format="PNG")
    
    with c2:
        # FIX: Improved formatting for Biographical Details (Issue 3)
        st.markdown('<div class="detail-meta-box">', unsafe_allow_html=True)
        st.markdown("### Biographical Details")
        st.markdown(f"""
        <ul class="bio-list">
            <li><strong>Species:</strong> {char.get('species', 'Unknown')}</li>
            <li><strong>Gender:</strong> {char.get('gender', 'Unknown')}</li>
            <li><strong>Origin:</strong> {char.get('origin', {}).get('name', 'Unknown')}</li>
            <li><strong>Last Known Location:</strong> {char.get('location', {}).get('name', 'Unknown')}</li>
            <li><strong>Type:</strong> {char.get('type') or 'N/A'}</li>
        </ul>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("## 📺 Episodes They Appeared In")
    episode_urls = char.get("episode", [])
    if episode_urls:
        st.caption(f"Appeared in {len(episode_urls)} episodes.")
        
        episodes = fetch_multiple(episode_urls, limit=len(episode_urls)) 
        
        for ep in episodes:
            st.markdown(
                f"""
                <div style="background-color: var(--card); padding: 10px 15px; border-radius: 8px; margin-bottom: 10px; border: 1px solid var(--border);">
                    <div style="font-weight: bold; font-size: 1.1em; color: var(--text);">{ep.get('name')}</div>
                    <div style="color: var(--muted); font-size: 0.9em;">{ep.get('episode')} &bull; Air Date: {ep.get('air_date')}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("This character has no recorded episode appearances.")

def render_character_list():
    """Renders the Character Directory with search, filters, and pagination."""
    st.subheader("Character Directory")

    # --- Filters (Top Bar) ---
    with st.container():
        st.markdown('<div class="filterbar">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([2.5, 1.2, 1.2, 1.5])
        with c1:
            st.text_input("Search name", placeholder="e.g., Rick Sanchez", key="q_name", on_change=reset_char_page)
        with c2:
            # FIX: Added 'Select' placeholder text (Issue 2)
            st.selectbox("Status", ["", "alive", "dead", "unknown"], key="q_status", on_change=reset_char_page, format_func=lambda x: 'Select Status' if x == '' else x)
        with c3:
            st.text_input("Species", placeholder="e.g., Human, Alien", key="q_species", on_change=reset_char_page)
        with c4:
            # FIX: Added 'Select' placeholder text (Issue 2)
            st.selectbox("Gender", ["", "male", "female", "genderless", "unknown"], key="q_gender", on_change=reset_char_page, format_func=lambda x: 'Select Gender' if x == '' else x)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- API Params ---
    params = {"page": st.session_state.char_page}
    if st.session_state.q_name: params["name"] = st.session_state.q_name
    if st.session_state.q_status: params["status"] = st.session_state.q_status
    if st.session_state.q_species: params["species"] = st.session_state.q_species
    if st.session_state.q_gender: params["gender"] = st.session_state.q_gender

    # --- API Call ---
    data = api_get("character", params)

    if "error" in data:
        st.error(data["error"])
        # If pagination causes an error (e.g., page 50 filtered to nothing), reset
        if st.session_state.char_page != 1:
            st.session_state.char_page = 1
            st.rerun()
    else:
        info = data.get("info", {})
        res = data.get("results", [])

        if res:
            # Grid Display
            st.markdown('<div class="grid">', unsafe_allow_html=True)
            cols = st.columns(4) 

            for i, ch in enumerate(res):
                with cols[i % 4]:
                    render_character_card(ch)
            
            st.markdown('</div>', unsafe_allow_html=True)

            # Bottom Pager (OUTSIDE the grid container to ensure full width)
            pager_controls(info, current_page_key="char_page", key_prefix="char_bottom")

        else:
            st.info("No characters found. Try adjusting your search or filters.")


def render_episodes():
    """Renders the Episodes tab with search and pagination."""
    st.subheader("Episodes")
    with st.container():
        st.markdown('<div class="filterbar">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2,1,1])
        with c1:
            ep_name = st.text_input("Episode name", placeholder="e.g., Pilot", key="ep-name")
        with c2:
            ep_code = st.text_input("Code", placeholder="e.g., S01E01", key="ep-code")
        with c3:
            st.session_state.ep_page = st.number_input("Page", min_value=1, value=st.session_state.ep_page, step=1, key="ep-page-input")
        st.markdown('</div>', unsafe_allow_html=True)

    params = {"page": int(st.session_state.ep_page)}
    if ep_name: params["name"] = ep_name
    if ep_code: params["episode"] = ep_code

    data = api_get("episode", params)
    if "error" in data:
        st.error(data["error"])
    else:
        info = data.get("info", {})
        res = data.get("results", [])
        if res:
            for ep in res:
                with st.container():
                    st.markdown(f"#### {ep['name']} — {ep['episode']}")
                    st.caption(f"Air date: {ep['air_date']}  •  ID: {ep['id']}")
                    
                    chars = fetch_multiple(ep.get("characters", []), limit=10)
                    if chars:
                        chips = " ".join([f"<span class='pill'>{c['name']}</span>" for c in chars])
                        st.markdown(f"**Characters:** {chips}", unsafe_allow_html=True)
                st.markdown("---")
            pager_controls(info, current_page_key="ep_page", key_prefix="ep_bottom")
        else:
            st.info("No episodes matched your query.")


def render_locations():
    """Renders the Locations tab with search and pagination."""
    st.subheader("Locations")
    with st.container():
        st.markdown('<div class="filterbar">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2,1,1])
        with c1:
            loc_name = st.text_input("Location name", placeholder="e.g., Citadel of Ricks", key="loc-name")
        with c2:
            loc_type = st.text_input("Type", placeholder="e.g., Planet", key="loc-type")
        with c3:
            st.session_state.loc_page = st.number_input("Page", min_value=1, value=st.session_state.loc_page, step=1, key="loc-page-input")
        st.markdown('</div>', unsafe_allow_html=True)

    params = {"page": int(st.session_state.loc_page)}
    if loc_name: params["name"] = loc_name
    if loc_type: params["type"] = loc_type
    
    data = api_get("location", params)
    if "error" in data:
        st.error(data["error"])
    else:
        info = data.get("info", {})
        res = data.get("results", [])
        if res:
            for loc in res:
                st.markdown(f"#### {loc['name']} — {loc['type']}")
                st.caption(f"Dimension: {loc['dimension']}  •  ID: {loc['id']}")
                
                residents = fetch_multiple(loc.get("residents", []), limit=10)
                if residents:
                    chips = " ".join([f"<span class='pill'>{r['name']}</span>" for r in residents])
                    st.markdown(f"**Residents:** {chips}", unsafe_allow_html=True)
                st.markdown("---")
            pager_controls(info, current_page_key="loc_page", key_prefix="loc_bottom")
        else:
            st.info("No locations matched your query.")


# ==============================================================================
# 5. CSS STYLES
# ==============================================================================

CUSTOM_CSS = f"""
<style>
/* Theme Variables */
:root {{
    --brand: #09f;
    --ok: #22c55e;
    --warn: #eab308;
    --bad: #ef4444;
    --ring: 0 0 0 2px rgba(0,153,255,.25);
}}

{'/* Dark Theme */' if st.session_state.theme == 'dark' else '/* Light Theme */'}
:root {{
    /* Theme Colors */
    --background: {'#0b0f14' if st.session_state.theme == 'dark' else '#ffffff'};
    --card: {'#111723' if st.session_state.theme == 'dark' else '#f0f2f6'};
    --text: {'#e5e7eb' if st.session_state.theme == 'dark' else '#1f2937'};
    --muted: {'#94a3b8' if st.session_state.theme == 'dark' else '#4b5563'};
    --border: {'rgba(255,255,255,.08)' if st.session_state.theme == 'dark' else 'rgba(0,0,0,.15)'};
    --filterbar-bg: {'rgba(15,23,36,.8)' if st.session_state.theme == 'dark' else 'rgba(255,255,255,.95)'};
    --view-details-bg: #00B0C8; /* Highlight color */
    --view-details-text: #0b0f14;
    
    /* Input/Select Colors */
    --input-bg: {'#1e293b' if st.session_state.theme == 'dark' else '#ffffff'};
    --input-text: var(--text);
}}

/* Apply background to the entire body/app */
.stApp {{
    background-color: var(--background);
    color: var(--text);
}}

/* Streamlit Widget Overrides (Fix for Issue 1: Filters in Light Mode) */
.stTextInput > div > div > input,
.stSelectbox > div > div > div > div,
.stNumberInput > div > div > input {{
    background-color: var(--input-bg) !important;
    color: var(--input-text) !important;
    border: 1px solid var(--border) !important;
}}
.stSelectbox > div > div > div > div {{
    border-radius: 10px !important;
}}

/* Tabs Styling (Issue 2) */
div[data-testid="stTabs"] {{
    border-bottom: 2px solid var(--border);
    margin-bottom: 1.5rem;
}}
div[data-testid="stTab"] button {{
    color: var(--muted) !important;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 700; /* Increased font weight */
    font-size: 1.2em; /* Increased font size */
    padding: 10px 20px; /* Increased spacing/padding */
    margin-right: 10px;
}}
div[data-testid="stTab"][aria-selected="true"] button {{
    color: var(--text) !important;
    border-bottom: 3px solid var(--brand) !important;
}}


/* App container padding */
.block-container {{padding-top: 1.5rem; max-width: 1200px;}}

/* Headings */
h1, h2, h3, h4 {{letter-spacing: .3px; color: var(--text);}}

/* Detail Page Title Spacing (Issue 1) */
.detail-title {{
    margin-top: 5px; /* Reduced space after the '---' and before the title */
    margin-bottom: 0.5rem;
}}

/* Filter/Search Bar Styling */
.filterbar {{
    position: sticky; top: 0; z-index: 5;
    background: var(--filterbar-bg);
    backdrop-filter: blur(6px);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 18px;
    box-shadow: 0 6px 24px rgba(0,0,0,.25);
}}

/* Card Grid Layout */
.grid {{
    display: grid; 
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); 
    gap: 16px;
}}

/* Character Card Styling */
.card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
    position: relative; 
}}
.card:hover {{
    transform: translateY(-3px); 
    box-shadow: 0 10px 30px rgba(0,0,0,.35); 
    border-color: var(--brand); 
}}
.card img {{width: 100%; height: 240px; object-fit: cover; display: block;}}
.card-body {{padding: 12px 14px 14px 14px;}}
.card-title {{font-weight: 700; margin: 2px 0 6px 0; color: var(--text);}}
.meta {{color: var(--muted); font-size: 13px}}

/* Status Badge */
.badge {{
    position:absolute; top:10px; left:10px; padding:6px 10px; border-radius:999px; 
    font-size:12px; font-weight:700; color:var(--background); background:#cbd5e1; z-index: 2;
}}
.badge.alive{{background: var(--ok);}}
.badge.dead{{background: var(--bad);}}
.badge.unknown{{background: var(--warn);}}
.card-figure{{position:relative}}


/* Detail Page Status Fix */
.status-container {{
    display: flex; 
    align-items: center; 
    margin-bottom: 1rem;
}}
.status-container .status-label {{
    color: var(--muted);
    font-size: 1.2em;
    font-weight: 500;
    margin-right: 10px;
}}
.status-container .badge {{
    position: static; /* Override absolute positioning */
    transform: none;
    color: var(--background); /* Text color inside badge */
}}

/* Detail Page Biographical List Formatting */
.bio-list {{
    list-style: none;
    padding-left: 0;
    margin-top: 10px;
    font-size: 1.05em; /* Slightly larger text */
}}
.bio-list li {{
    margin-bottom: 10px; /* Increased vertical space */
    color: var(--text);
    padding-left: 1.2em; 
    text-indent: -1.2em;
}}
.bio-list li::before {{
    content: "•";
    color: var(--brand); 
    font-weight: bold;
    display: inline-block; 
    width: 1.2em; 
}}
.bio-list li strong {{
    font-weight: 700; /* Ensure strong tag is truly bold */
}}

/* General Button Styles */
div[data-testid="stVerticalBlock"] .stButton > button {{ 
    border-radius: 10px;
    border: 1px solid var(--border);
    color: var(--text);
    min-height: 32px;
    height: auto;
    padding: 6px 12px;
    font-size: 14px;
    max-width: none;
    display: block;
    /* Removed default gradient to ensure dynamic color shines */
    background: var(--card); 
}}
div[data-testid="stVerticalBlock"] .stButton > button:hover {{
    filter: brightness(1.1);
}}

/* Back to Characters Button Width */
.back-btn-wrapper .stButton > button {{
    max-width: 170px;
    font-weight: 600;
}}

/* View Details Button Highlight (Issue 1) */
/* Targets the specific button wrapper using the dynamically set CSS variable */
div:has(> .stButton > button:contains("View Details")) > button {{
    background-color: var(--status-color-dyn) !important; 
    color: var(--view-details-text) !important; /* Ensure black text on color */
    font-weight: bold;
    border-color: var(--status-color-dyn) !important;
    /* Added hover effect for better appeal */
    box-shadow: 0 4px 10px rgba(0,0,0,0.25);
    transition: all 0.2s ease;
}}
div:has(> .stButton > button:contains("View Details")) > button:hover {{
    filter: brightness(1.1);
    box-shadow: 0 6px 15px rgba(0,0,0,0.35);
}}


/* Theme Toggle Button Style */
.theme-toggle-wrapper .stButton > button {{
    background: var(--card);
    color: var(--text);
    max-width: 50px;
    padding: 6px;
    line-height: 1;
    font-size: 16px;
}}

/* Detailed Meta Box */
.detail-meta-box {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
}}

/* HIDE 'Menu' button for all components (Issue 1) */
.stApp [data-testid="StyledFullScreenButton"],
.stApp [data-testid="stBlock"] [data-testid="stBlock"] > [data-testid="stBlock"] > div > [data-testid="StyledFullScreenButton"] {{
    display: none !important;
}}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================================
# 6. MAIN APPLICATION ENTRY POINT
# ==============================================================================

# Header with Title and Theme Toggle
header_cols = st.columns([1, 0.05])
with header_cols[0]:
    st.title("🧪 Rickipedia")
    st.caption("A sleek encyclopedia of all things **Rick & Morty** — characters, episodes, and locations.")
with header_cols[1]:
    # Theme Toggle Button (Issue 2)
    st.markdown('<div class="theme-toggle-wrapper">', unsafe_allow_html=True)
    theme_icon = "🌞" if st.session_state.theme == 'dark' else "🌙"
    st.button(theme_icon, on_click=toggle_theme, key="theme_toggle")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Main Tabs (Home tab removed, starting directly with Characters) ---
tabs = st.tabs(["Characters", "Episodes", "Locations"])

# --- Characters Tab Logic (Handles List OR Detail View) ---
with tabs[0]:
    # Show the detail page if a character is selected
    if st.session_state.page_view == 'Character_Detail' and st.session_state.selected_char_id is not None:
        render_character_detail_page(st.session_state.selected_char_id)
    else:
        render_character_list()

# --- Episodes Tab ---
with tabs[1]:
    render_episodes()

# --- Locations Tab ---
with tabs[2]:
    render_locations()

# ==============================================================================
# 7. FUNKY FOOTER (NEW)
# ==============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; font-size: 1.1em; color: var(--muted); padding-top: 10px;">
    .𖥔 ݁ ˖🔫.𖥔.👴🏼🥼.˖.👽.˖🥒.𖥔 📟݁ ˖🪐.𖥔. 🛸.˖.𖥔<br>
    <br>🌑🌒🌓🌔🌕
            <br>
    Made with♥️
</div>
""", unsafe_allow_html=True)
