import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Theme state
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True


# -----------------------------------------------------------------------------
# Visual theme
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #0d0912;
        --bg-soft: #130d1b;
        --panel: #171020;
        --panel-2: #1d1428;
        --border: #352442;
        --purple: #a855f7;
        --purple-2: #7c3aed;
        --purple-soft: #2b173d;
        --text: #f7f4fb;
        --muted: #a99eb5;
        --green: #34d399;
        --amber: #fbbf24;
        --red: #fb7185;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 15% 0%, rgba(124,58,237,.16), transparent 30%),
            radial-gradient(circle at 90% 15%, rgba(168,85,247,.08), transparent 25%),
            var(--bg);
        color: var(--text);
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #120d19 0%, #0d0912 100%);
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.15rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: .8rem;
        padding: .35rem .25rem 1.1rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1rem;
    }

    .brand-icon {
        width: 42px;
        height: 42px;
        display: grid;
        place-items: center;
        border-radius: 12px;
        background: linear-gradient(135deg, #7c3aed, #a855f7);
        box-shadow: 0 8px 30px rgba(124,58,237,.35);
        font-size: 1.2rem;
    }

    .brand-title {
        color: #fff;
        font-size: 1.05rem;
        font-weight: 800;
        margin: 0;
    }

    .brand-subtitle {
        color: var(--muted);
        font-size: .72rem;
        margin-top: .15rem;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] > label {
        border-radius: 10px;
        padding: .55rem .65rem;
        margin: .15rem 0;
        transition: all .2s ease;
        border: 1px solid transparent;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] > label:hover {
        background: rgba(168,85,247,.08);
        border-color: rgba(168,85,247,.18);
        transform: translateX(2px);
    }

    /* Hide default radio circles in nav */
    section[data-testid="stSidebar"] [role="radiogroup"] [data-testid="stWidgetLabel"] {display:none;}

    /* Hero */
    .hero {
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1.5rem 1.6rem;
        background:
            linear-gradient(135deg, rgba(124,58,237,.15), rgba(168,85,247,.06)),
            var(--panel);
        box-shadow: 0 18px 45px rgba(0,0,0,.18);
        margin-bottom: 1.1rem;
        animation: fadeUp .45s ease both;
        position: relative;
        overflow: hidden;
    }

    .hero:after {
        content: '';
        position: absolute;
        width: 180px;
        height: 180px;
        border-radius: 999px;
        background: rgba(168,85,247,.11);
        filter: blur(6px);
        right: -40px;
        top: -80px;
    }

    .eyebrow {
        color: #c084fc;
        text-transform: uppercase;
        letter-spacing: .14em;
        font-weight: 700;
        font-size: .72rem;
        margin-bottom: .45rem;
    }

    .hero h1 {
        color: #fff !important;
        font-size: clamp(1.65rem, 3vw, 2.45rem);
        line-height: 1.08;
        margin: 0 0 .45rem 0;
        font-weight: 800;
    }

    .hero p {
        color: #c5bacf;
        margin: 0;
        max-width: 760px;
    }

    /* Section headings */
    h1, h2, h3, h4 { color: var(--text) !important; }
    h2, h3 { letter-spacing: -.02em; }
    p, label, .stCaption { color: #c8becf; }

    .section-label {
        color: #bcaec8;
        font-size: .8rem;
        font-weight: 700;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin: 1.3rem 0 .7rem;
    }

    /* Metric cards */
    .metric-card {
        position: relative;
        border: 1px solid var(--border);
        border-radius: 16px;
        background: linear-gradient(180deg, #1a1224, #15101d);
        padding: 1.05rem 1.1rem;
        min-height: 125px;
        overflow: hidden;
        box-shadow: 0 12px 26px rgba(0,0,0,.14);
        transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
        animation: fadeUp .48s ease both;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        border-color: #65407e;
        box-shadow: 0 16px 32px rgba(0,0,0,.25);
    }

    .metric-top {
        display:flex;
        align-items:center;
        justify-content:space-between;
        margin-bottom:.8rem;
    }

    .metric-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display:grid;
        place-items:center;
        background: var(--purple-soft);
        color: #d8b4fe;
        font-size: 1rem;
    }

    .metric-label {
        color: #a99eb5;
        font-size:.78rem;
        font-weight:600;
    }

    .metric-value {
        color:#fff;
        font-weight:800;
        font-size:1.75rem;
        letter-spacing:-.04em;
    }

    .metric-accent-purple { box-shadow: inset 0 2px 0 #8b5cf6, 0 12px 26px rgba(0,0,0,.14); }
    .metric-accent-green { box-shadow: inset 0 2px 0 #34d399, 0 12px 26px rgba(0,0,0,.14); }
    .metric-accent-amber { box-shadow: inset 0 2px 0 #fbbf24, 0 12px 26px rgba(0,0,0,.14); }
    .metric-accent-red { box-shadow: inset 0 2px 0 #fb7185, 0 12px 26px rgba(0,0,0,.14); }

    /* Panels */
    .panel {
        border: 1px solid var(--border);
        border-radius: 16px;
        background: rgba(23,16,32,.9);
        padding: 1.1rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 14px 34px rgba(0,0,0,.12);
        animation: fadeUp .5s ease both;
    }

    .panel-title {
        color:#fff;
        font-size:1rem;
        font-weight:750;
        margin-bottom:.25rem;
    }

    .panel-subtitle {
        color:var(--muted);
        font-size:.82rem;
        margin-bottom:.9rem;
    }

    /* Dataframes */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 14px;
        overflow: hidden;
        background: #120d19;
    }

    /* Inputs */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"],
    .stNumberInput input,
    .stTextInput input {
        background: #15101d !important;
        border-color: var(--border) !important;
        color: #fff !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 1px #8b5cf6 !important;
    }

    /* Buttons */
    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        border: 1px solid #674284 !important;
        background: linear-gradient(135deg, #7c3aed, #9333ea) !important;
        color: white !important;
        transition: transform .18s ease, box-shadow .18s ease !important;
        min-height: 42px;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 22px rgba(124,58,237,.3) !important;
    }

    /* Alerts */
    div[data-testid="stAlert"] {
        border-radius: 12px;
        border: 1px solid var(--border);
    }

    /* Status cards */
    .status-row {
        display:grid;
        grid-template-columns: repeat(3, 1fr);
        gap:.7rem;
        margin-top:.7rem;
    }

    .status-box {
        border:1px solid var(--border);
        border-radius:12px;
        padding:.85rem;
        background:#140e1c;
    }

    .status-box b { display:block; color:#fff; font-size:1.2rem; margin-top:.15rem; }
    .status-box small { color:var(--muted); }
    .status-good { border-color: rgba(52,211,153,.25); }
    .status-low { border-color: rgba(251,191,36,.27); }
    .status-out { border-color: rgba(251,113,133,.28); }

    /* Project footer */
    .project-strip {
        margin-top: 1.2rem;
        border:1px solid var(--border);
        border-radius:14px;
        padding:.9rem 1rem;
        background:rgba(23,16,32,.75);
        color:var(--muted);
        font-size:.78rem;
        display:flex;
        justify-content:space-between;
        gap:1rem;
        flex-wrap:wrap;
    }

    @keyframes fadeUp {
        from {opacity:0; transform:translateY(10px)}
        to {opacity:1; transform:translateY(0)}
    }

    @media (max-width: 800px) {
        .status-row { grid-template-columns: 1fr; }
        .hero { padding: 1.15rem; }
        .metric-card { min-height: 110px; }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *:before, *:after {
            animation-duration: .01ms !important;
            transition-duration: .01ms !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Light / dark mode overrides
# -----------------------------------------------------------------------------
_dark = st.session_state.dark_mode
_theme = {
    "bg": "#0d0912" if _dark else "#f7f5fb",
    "bg_soft": "#130d1b" if _dark else "#eee8f5",
    "panel": "#171020" if _dark else "#ffffff",
    "panel_2": "#1d1428" if _dark else "#faf7fd",
    "border": "#352442" if _dark else "#ded5e7",
    "text": "#f7f4fb" if _dark else "#211627",
    "muted": "#a99eb5" if _dark else "#706377",
    "body": "#c8becf" if _dark else "#574c5f",
    "sidebar": "#120d19" if _dark else "#ffffff",
    "sidebar_end": "#0d0912" if _dark else "#f4eff8",
    "input": "#15101d" if _dark else "#ffffff",
    "table": "#120d19" if _dark else "#ffffff",
    "status": "#140e1c" if _dark else "#faf7fc",
    "hero_text": "#ffffff" if _dark else "#211627",
    "hero_sub": "#c5bacf" if _dark else "#6f6277",
    "shadow": "rgba(0,0,0,.22)" if _dark else "rgba(52,35,65,.10)",
    "glow1": "rgba(124,58,237,.16)" if _dark else "rgba(124,58,237,.09)",
    "glow2": "rgba(168,85,247,.08)" if _dark else "rgba(168,85,247,.05)",
}

st.markdown(
    f"""
    <style>
    :root {{
        --bg: {_theme['bg']};
        --bg-soft: {_theme['bg_soft']};
        --panel: {_theme['panel']};
        --panel-2: {_theme['panel_2']};
        --border: {_theme['border']};
        --text: {_theme['text']};
        --muted: {_theme['muted']};
    }}

    .stApp {{
        background:
            radial-gradient(circle at 15% 0%, {_theme['glow1']}, transparent 30%),
            radial-gradient(circle at 90% 15%, {_theme['glow2']}, transparent 25%),
            {_theme['bg']} !important;
        color: {_theme['text']} !important;
    }}

    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {_theme['sidebar']} 0%, {_theme['sidebar_end']} 100%) !important;
        border-right: 1px solid {_theme['border']} !important;
    }}

    .brand-title, h1, h2, h3, h4, .panel-title, .metric-value, .status-box b {{
        color: {_theme['text']} !important;
    }}

    .brand-subtitle, .metric-label, .panel-subtitle, .status-box small,
    .project-strip, .section-label, .stCaption {{
        color: {_theme['muted']} !important;
    }}

    p, label, section[data-testid="stSidebar"] span {{
        color: {_theme['body']} !important;
    }}

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {{
        color: {_theme['text']} !important;
    }}

    .hero {{
        background:
            linear-gradient(135deg, {_theme['glow1']}, {_theme['glow2']}),
            {_theme['panel']} !important;
        border-color: {_theme['border']} !important;
        box-shadow: 0 18px 45px {_theme['shadow']} !important;
    }}

    .hero h1 {{ color: {_theme['hero_text']} !important; }}
    .hero p {{ color: {_theme['hero_sub']} !important; }}

    .metric-card {{
        background: linear-gradient(180deg, {_theme['panel_2']}, {_theme['panel']}) !important;
        border-color: {_theme['border']} !important;
        box-shadow: 0 12px 26px {_theme['shadow']} !important;
    }}

    .panel, .project-strip {{
        background: {_theme['panel']} !important;
        border-color: {_theme['border']} !important;
        box-shadow: 0 14px 34px {_theme['shadow']} !important;
    }}

    .status-box {{
        background: {_theme['status']} !important;
        border-color: {_theme['border']} !important;
    }}

    div[data-testid="stDataFrame"] {{
        background: {_theme['table']} !important;
        border-color: {_theme['border']} !important;
    }}

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"],
    .stNumberInput input,
    .stTextInput input {{
        background: {_theme['input']} !important;
        color: {_theme['text']} !important;
        border-color: {_theme['border']} !important;
    }}

    input {{
        color: {_theme['text']} !important;
        -webkit-text-fill-color: {_theme['text']} !important;
    }}

    input::placeholder {{
        color: {_theme['muted']} !important;
        opacity: .75 !important;
    }}

    div[data-baseweb="select"] span {{ color: {_theme['text']} !important; }}

    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"] {{
        background: {_theme['panel']} !important;
        color: {_theme['text']} !important;
    }}

    li[role="option"] {{
        background: {_theme['panel']} !important;
        color: {_theme['text']} !important;
    }}

    li[role="option"]:hover {{
        background: {_theme['panel_2']} !important;
    }}

    hr {{ border-color: {_theme['border']} !important; }}

    /* Keep primary controls legible in both modes */
    .stButton > button, .stFormSubmitButton > button {{
        color: white !important;
    }}

    /* Streamlit toggle track / labels */
    div[data-testid="stToggle"] label p {{
        color: {_theme['text']} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

SAMPLE_PRODUCTS = [
    {"name": "Pen", "category": "Stationery", "quantity": 50, "price": 10.0},
    {"name": "Notebook", "category": "Stationery", "quantity": 30, "price": 50.0},
    {"name": "Water Bottle", "category": "Utility", "quantity": 12, "price": 120.0},
]

if "inventory" not in st.session_state:
    st.session_state.inventory = [item.copy() for item in SAMPLE_PRODUCTS]


def currency(value: float) -> str:
    return f"₹{value:,.0f}"


def inventory_df(items=None) -> pd.DataFrame:
    source = st.session_state.inventory if items is None else items
    return pd.DataFrame(source)


def totals():
    items = st.session_state.inventory
    total_products = len(items)
    total_units = sum(item["quantity"] for item in items)
    total_value = sum(item["quantity"] * item["price"] for item in items)
    low_stock = sum(1 for item in items if item["quantity"] < 10)
    return total_products, total_units, total_value, low_stock


def status_for(quantity: int, threshold: int = 10) -> str:
    if quantity == 0:
        return "Out of Stock"
    if quantity < threshold:
        return "Low Stock"
    return "Healthy"


def display_table(items):
    if not items:
        st.info("No products to display.")
        return

    df = pd.DataFrame(items).copy()
    df["Status"] = df["quantity"].apply(status_for)
    df["price"] = df["price"].map(currency)
    df.columns = ["Product", "Category", "Quantity", "Price", "Status"]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Product": st.column_config.TextColumn("Product", width="medium"),
            "Category": st.column_config.TextColumn("Category", width="medium"),
            "Quantity": st.column_config.NumberColumn("Quantity", width="small"),
            "Price": st.column_config.TextColumn("Price", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
        },
    )


def metric_card(icon, label, value, accent="purple"):
    st.markdown(
        f"""
        <div class="metric-card metric-accent-{accent}">
            <div class="metric-top">
                <div class="metric-label">{label}</div>
                <div class="metric-icon">{icon}</div>
            </div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, subtitle, eyebrow="Inventory Management System"):
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">📦</div>
            <div>
                <div class="brand-title">Inventory System</div>
                <div class="brand-subtitle">AI/ML Semester I Project</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    theme_value = st.toggle(
        "🌙 Dark mode",
        value=st.session_state.dark_mode,
        key="theme_toggle",
    )
    if theme_value != st.session_state.dark_mode:
        st.session_state.dark_mode = theme_value
        st.rerun()

    operation = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Add Product",
            "Search Product",
            "Update Product",
            "Delete Product",
            "Low-Stock View",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption("QUICK ACTION")
    if st.button("↻ Reset Demo Inventory", use_container_width=True):
        st.session_state.inventory = [item.copy() for item in SAMPLE_PRODUCTS]
        st.success("Demo inventory restored.")
        st.rerun()

    st.markdown("---")
    st.caption("PROJECT TEAM")
    st.markdown("**Vanshika** · 267111")
    st.markdown("**Asim** · 267136")
    st.markdown("**Jonathan** · 267108")
    st.caption("Thakur College of Science and Commerce")


# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------
if operation == "Dashboard":
    page_header(
        "Inventory Dashboard",
        "Organize Stock. Process Data. Manage Better. Monitor products, inventory value and low-stock items from one place.",
        "Overview",
    )

    total_products, total_units, total_value, low_stock = totals()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("▦", "Products", f"{total_products}", "purple")
    with c2:
        metric_card("▤", "Total Units", f"{total_units:,}", "green")
    with c3:
        metric_card("₹", "Inventory Value", currency(total_value), "purple")
    with c4:
        metric_card("!", "Low Stock", f"{low_stock}", "amber" if low_stock else "green")

    st.markdown('<div class="section-label">Current Inventory</div>', unsafe_allow_html=True)

    left, right = st.columns([2.15, 0.85], gap="large")
    with left:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">Product Overview</div>
                <div class="panel-subtitle">Current products with quantity, price and stock status.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        display_table(st.session_state.inventory)

    with right:
        healthy = sum(1 for x in st.session_state.inventory if x["quantity"] >= 10)
        low = sum(1 for x in st.session_state.inventory if 0 < x["quantity"] < 10)
        out = sum(1 for x in st.session_state.inventory if x["quantity"] == 0)

        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-title">Stock Health</div>
                <div class="panel-subtitle">Quick status summary based on a 10-unit low-stock threshold.</div>
                <div class="status-row">
                    <div class="status-box status-good"><small>Healthy</small><b>{healthy}</b></div>
                    <div class="status-box status-low"><small>Low</small><b>{low}</b></div>
                    <div class="status-box status-out"><small>Out</small><b>{out}</b></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">How it works</div>
                <div class="panel-subtitle">Use the sidebar to add, search, update or delete products. The dashboard recalculates totals automatically.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

elif operation == "Add Product":
    page_header(
        "Add Product",
        "Create a new inventory record with product name, category, quantity and price.",
        "Inventory Operation",
    )

    st.markdown('<div class="section-label">Product Details</div>', unsafe_allow_html=True)
    with st.form("add_product_form", clear_on_submit=True):
        left, right = st.columns(2, gap="large")
        with left:
            name = st.text_input("Product Name", placeholder="e.g. Marker")
            quantity = st.number_input("Quantity", min_value=0, step=1, value=0)
        with right:
            category = st.text_input("Category", placeholder="e.g. Stationery")
            price = st.number_input("Price (₹)", min_value=0.0, step=1.0, value=0.0)

        submitted = st.form_submit_button("＋ Add Product", use_container_width=True)

    if submitted:
        if not name.strip() or not category.strip():
            st.error("Product name and category are required.")
        else:
            st.session_state.inventory.append(
                {
                    "name": name.strip(),
                    "category": category.strip(),
                    "quantity": int(quantity),
                    "price": float(price),
                }
            )
            st.success(f"{name.strip()} added successfully.")

elif operation == "Search Product":
    page_header(
        "Search Product",
        "Find an existing inventory item quickly using its product name or keyword.",
        "Inventory Operation",
    )

    query = st.text_input("Search inventory", placeholder="Type a product name, e.g. pen")
    if query.strip():
        results = [
            item
            for item in st.session_state.inventory
            if query.lower() in item["name"].lower()
        ]
        st.markdown(
            f'<div class="section-label">{len(results)} result(s) found</div>',
            unsafe_allow_html=True,
        )
        if results:
            display_table(results)
        else:
            st.warning("No matching product found.")
    else:
        st.info("Enter a product name or keyword to search the inventory.")

elif operation == "Update Product":
    page_header(
        "Update Product",
        "Change the quantity or price of an existing product and instantly refresh inventory totals.",
        "Inventory Operation",
    )

    if not st.session_state.inventory:
        st.info("There are no products to update.")
    else:
        names = [item["name"] for item in st.session_state.inventory]
        selected = st.selectbox("Select Product", names)
        index = names.index(selected)
        item = st.session_state.inventory[index]

        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-title">{item['name']}</div>
                <div class="panel-subtitle">Category: {item['category']} · Current quantity: {item['quantity']} · Current price: {currency(item['price'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("update_product_form"):
            c1, c2 = st.columns(2, gap="large")
            with c1:
                new_qty = st.number_input(
                    "New Quantity",
                    min_value=0,
                    value=int(item["quantity"]),
                    step=1,
                )
            with c2:
                new_price = st.number_input(
                    "New Price (₹)",
                    min_value=0.0,
                    value=float(item["price"]),
                    step=1.0,
                )
            update = st.form_submit_button("✓ Update Product", use_container_width=True)

        if update:
            st.session_state.inventory[index]["quantity"] = int(new_qty)
            st.session_state.inventory[index]["price"] = float(new_price)
            st.success(f"{selected} updated successfully.")

elif operation == "Delete Product":
    page_header(
        "Delete Product",
        "Remove an inventory record that is no longer required.",
        "Inventory Operation",
    )

    if not st.session_state.inventory:
        st.info("There are no products to delete.")
    else:
        names = [item["name"] for item in st.session_state.inventory]
        selected = st.selectbox("Select Product", names)
        selected_item = next(x for x in st.session_state.inventory if x["name"] == selected)

        st.markdown(
            f"""
            <div class="panel" style="border-color: rgba(251,113,133,.35);">
                <div class="panel-title">Delete {selected}?</div>
                <div class="panel-subtitle">Category: {selected_item['category']} · Quantity: {selected_item['quantity']} · Price: {currency(selected_item['price'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.warning("This action removes the product from the current inventory session.")

        if st.button("Delete Product", type="primary", use_container_width=True):
            st.session_state.inventory = [
                item for item in st.session_state.inventory if item["name"] != selected
            ]
            st.success(f"{selected} deleted successfully.")
            st.rerun()

elif operation == "Low-Stock View":
    page_header(
        "Low-Stock View",
        "Identify products that need attention by comparing their quantity with a configurable threshold.",
        "Stock Monitoring",
    )

    threshold = st.slider("Low-stock threshold", min_value=1, max_value=50, value=10, step=1)
    low_items = [
        item for item in st.session_state.inventory if item["quantity"] < threshold
    ]

    total_products, total_units, total_value, _ = totals()
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("!", "Below Threshold", len(low_items), "amber" if low_items else "green")
    with c2:
        metric_card("#", "Threshold", f"< {threshold} units", "purple")
    with c3:
        metric_card("▦", "Total Products", total_products, "purple")

    st.markdown('<div class="section-label">Products Requiring Attention</div>', unsafe_allow_html=True)
    if low_items:
        display_table(low_items)
    else:
        st.success("No products are below the selected low-stock threshold.")


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="project-strip">
        <span><b>Thakur College of Science and Commerce</b> · Department of Artificial Intelligence and Machine Learning</span>
        <span>B.Sc. AI/ML · Semester I · Academic Year 2026–2027</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Academic prototype: inventory data is stored in the current Streamlit session and may reset when the application restarts."
)
