"""
StockPilot — Inventory Management System
A Python/Streamlit app with a sidebar-driven dashboard layout,
teal & slate color scheme, and inline spreadsheet-style editing.
"""

import streamlit as st
import pandas as pd
from db import (
    init_db, register_user, authenticate_user, add_item, update_item,
    delete_item, get_items, get_categories, get_stats,
)

st.set_page_config(page_title="StockPilot — Inventory Management",
                    page_icon="🧭", layout="wide", initial_sidebar_state="expanded")

init_db()

# ---------------------------------------------------------------------------
# THEME / CSS  — teal & slate, card-free, spreadsheet-style dashboard
# ---------------------------------------------------------------------------
TEAL = "#0D9488"
TEAL_DARK = "#0F766E"
SLATE = "#1E293B"
SLATE_SOFT = "#475569"
BG = "#F8FAFC"
BORDER = "#E2E8F0"
AMBER = "#D97706"
RED = "#DC2626"

st.markdown(f"""
<style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stApp {{ background-color: {BG}; }}
    .block-container {{ padding-top: 1.6rem; padding-bottom: 2rem; }}

    section[data-testid="stSidebar"] {{
        background-color: {SLATE}; padding-top: 0.5rem;
    }}
    section[data-testid="stSidebar"] * {{ color: #E2E8F0 !important; }}
    section[data-testid="stSidebar"] .stRadio label {{ font-size: 0.95rem; }}
    section[data-testid="stSidebar"] hr {{ border-color: #334155; }}

    .brand-row {{ display:flex; align-items:center; gap:0.6rem; padding: 0.4rem 0 1.1rem 0; }}
    .brand-mark {{
        width:36px; height:36px; border-radius:8px; background:{TEAL};
        display:flex; align-items:center; justify-content:center; font-size:1.2rem;
    }}
    .brand-word {{ font-size:1.15rem; font-weight:800; letter-spacing:-0.01em; color:white !important; }}
    .brand-tag {{ font-size:0.72rem; color:#94A3B8 !important; margin-top:-4px;}}

    h1, h2, h3 {{ color: {SLATE}; font-weight:800; letter-spacing:-0.01em; }}
    .page-title {{ font-size:1.7rem; font-weight:800; color:{SLATE}; margin-bottom:0.1rem; }}
    .page-sub {{ color:{SLATE_SOFT}; margin-bottom:1.3rem; font-size:0.95rem; }}

    /* KPI strip */
    div[data-testid="stMetric"] {{
        background:white; border:1px solid {BORDER}; border-left:4px solid {TEAL};
        border-radius:10px; padding:0.9rem 1.1rem;
    }}
    div[data-testid="stMetricLabel"] {{ color:{SLATE_SOFT}; }}
    div[data-testid="stMetricValue"] {{ color:{SLATE}; }}

    .pill-ok {{ background:#D1FAE5; color:#065F46; padding:2px 10px; border-radius:6px; font-size:0.78rem; font-weight:700;}}
    .pill-low {{ background:#FEF3C7; color:#92400E; padding:2px 10px; border-radius:6px; font-size:0.78rem; font-weight:700;}}
    .pill-out {{ background:#FEE2E2; color:#991B1B; padding:2px 10px; border-radius:6px; font-size:0.78rem; font-weight:700;}}

    div.stButton > button {{
        border-radius:6px; font-weight:700; border:1px solid {TEAL}; color:{TEAL};
    }}
    div.stButton > button[kind="primary"] {{ background:{TEAL}; color:white; border:none;}}
    div.stButton > button[kind="primary"]:hover {{ background:{TEAL_DARK}; }}

    .auth-wrap {{ max-width:420px; margin: 2.5rem auto 0 auto; background:white;
                  border:1px solid {BORDER}; border-radius:12px; padding:2rem; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 1.5rem; }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "nav" not in st.session_state:
    st.session_state.nav = "Dashboard"


def stock_pill(qty, reorder):
    if qty == 0:
        return '<span class="pill-out">Out of stock</span>'
    elif qty <= reorder:
        return '<span class="pill-low">Low stock</span>'
    return '<span class="pill-ok">In stock</span>'


# ---------------------------------------------------------------------------
# AUTH SCREEN (shown when logged out) — plain, centered, no marketing content
# ---------------------------------------------------------------------------
def render_auth():
    st.markdown(f"""
    <div class="brand-row" style="justify-content:center; margin-top:2rem;">
        <div class="brand-mark">🧭</div>
        <div>
            <div class="brand-word" style="color:{SLATE} !important;">StockPilot</div>
            <div class="brand-tag" style="color:{SLATE_SOFT} !important;">Inventory, under control.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)
    tab_login, tab_register = st.tabs(["Log In", "Create Account"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In", type="primary", use_container_width=True)
            if submitted:
                user = authenticate_user(email, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

    with tab_register:
        with st.form("register_form"):
            full_name = st.text_input("Full Name")
            reg_email = st.text_input("Email", key="reg_email")
            company = st.text_input("Warehouse / Business Name")
            reg_password = st.text_input("Password", type="password", key="reg_pw")
            submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
            if submitted:
                if not full_name or not reg_email or not reg_password:
                    st.error("Please fill in name, email, and password.")
                elif len(reg_password) < 4:
                    st.error("Password should be at least 4 characters.")
                else:
                    ok, msg = register_user(full_name, reg_email, company, reg_password)
                    if ok:
                        st.success(msg + " Switch to the Log In tab to continue.")
                    else:
                        st.error(msg)
    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# SIDEBAR (shown when logged in)
# ---------------------------------------------------------------------------
def render_sidebar(user):
    with st.sidebar:
        st.markdown(f"""
        <div class="brand-row">
            <div class="brand-mark">🧭</div>
            <div>
                <div class="brand-word">StockPilot</div>
                <div class="brand-tag">{user.get('company') or 'Your workspace'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        nav = st.radio("Navigate", ["Dashboard", "Inventory", "Add Item", "Reports"],
                        label_visibility="collapsed", key="nav_radio")
        st.session_state.nav = nav
        st.markdown("---")
        st.caption(f"Signed in as **{user['full_name']}**")
        if st.button("Log Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()


# ---------------------------------------------------------------------------
# DASHBOARD PAGE
# ---------------------------------------------------------------------------
def render_dashboard(user):
    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">A live snapshot of your inventory.</div>', unsafe_allow_html=True)

    stats = get_stats(user["id"])
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Items", stats["total_items"])
    k2.metric("Units in Stock", stats["total_quantity"])
    k3.metric("Low Stock Items", stats["low_stock"])
    k4.metric("Inventory Value", f"₹{stats['total_value']:,.2f}")

    if stats["low_stock"] > 0 or stats["out_of_stock"] > 0:
        st.warning(f"⚠️ {stats['low_stock']} item(s) low on stock, "
                   f"{stats['out_of_stock']} item(s) fully out of stock.")

    items = get_items(user["id"])
    if not items:
        st.info("No items yet — head to **Add Item** in the sidebar to start building your inventory.")
        return

    df = pd.DataFrame(items)

    left, right = st.columns([1.3, 1])
    with left:
        st.subheader("Stock by category")
        if df["category"].replace("", pd.NA).notna().any():
            by_cat = df.groupby(df["category"].replace("", "Uncategorized"))["quantity"].sum()
            st.bar_chart(by_cat)
        else:
            st.caption("Add categories to your items to see this breakdown.")

    with right:
        st.subheader("Needs attention")
        low_df = df[df["quantity"] <= df["reorder_level"]][["name", "quantity", "reorder_level"]]
        if low_df.empty:
            st.success("Everything is adequately stocked. ✅")
        else:
            low_df.columns = ["Item", "Qty", "Reorder at"]
            st.dataframe(low_df, hide_index=True, use_container_width=True)


# ---------------------------------------------------------------------------
# INVENTORY PAGE — spreadsheet-style inline editing via st.data_editor
# ---------------------------------------------------------------------------
def render_inventory(user):
    st.markdown('<div class="page-title">Inventory</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Search, filter, and edit stock directly in the table.</div>',
                unsafe_allow_html=True)

    f1, f2 = st.columns([2, 1])
    with f1:
        search = st.text_input("Search by name or SKU", placeholder="e.g. USB cable, SKU-1023")
    with f2:
        categories = ["All"] + get_categories(user["id"])
        category_filter = st.selectbox("Category", categories)

    items = get_items(user["id"], search=search, category_filter=category_filter)
    if not items:
        st.info("No items match your search/filter.")
        return

    df = pd.DataFrame(items)
    df["status"] = df.apply(lambda r: "Out of stock" if r["quantity"] == 0
                             else ("Low stock" if r["quantity"] <= r["reorder_level"] else "In stock"), axis=1)

    display_df = df[["id", "name", "sku", "category", "quantity", "unit_price",
                      "reorder_level", "supplier", "status"]].rename(columns={
        "id": "ID", "name": "Name", "sku": "SKU", "category": "Category",
        "quantity": "Qty", "unit_price": "Unit Price (₹)", "reorder_level": "Reorder At",
        "supplier": "Supplier", "status": "Status",
    })

    edited = st.data_editor(
        display_df,
        hide_index=True,
        use_container_width=True,
        disabled=["ID", "Status"],
        column_config={
            "ID": st.column_config.NumberColumn(width="small"),
            "Qty": st.column_config.NumberColumn(min_value=0, step=1),
            "Unit Price (₹)": st.column_config.NumberColumn(min_value=0.0, step=1.0, format="₹%.2f"),
            "Reorder At": st.column_config.NumberColumn(min_value=0, step=1),
            "Status": st.column_config.TextColumn(width="small"),
        },
        num_rows="fixed",
        key="inventory_editor",
    )

    c1, c2, c3 = st.columns([1, 1, 3])
    with c1:
        if st.button("💾 Save changes", type="primary", use_container_width=True):
            original = display_df.set_index("ID")
            changed = edited.set_index("ID")
            n = 0
            for item_id, row in changed.iterrows():
                orig = original.loc[item_id]
                if not row.equals(orig):
                    update_item(int(item_id), row["Name"], row["SKU"] or "", row["Category"] or "",
                                int(row["Qty"]), float(row["Unit Price (₹)"]), int(row["Reorder At"]),
                                row["Supplier"] or "")
                    n += 1
            st.success(f"Saved {n} change(s).")
            st.rerun()

    with c2:
        ids_to_delete = st.multiselect("Delete item(s) by ID", options=display_df["ID"].tolist())
        if ids_to_delete and st.button("🗑️ Delete selected", use_container_width=True):
            for item_id in ids_to_delete:
                delete_item(int(item_id))
            st.success(f"Deleted {len(ids_to_delete)} item(s).")
            st.rerun()

    csv = df[["name", "sku", "category", "quantity", "unit_price", "reorder_level", "supplier"]].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export as CSV", csv, "stockpilot_inventory.csv", "text/csv")


# ---------------------------------------------------------------------------
# ADD ITEM PAGE
# ---------------------------------------------------------------------------
def render_add_item(user):
    st.markdown('<div class="page-title">Add Item</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Add a new item to your inventory.</div>', unsafe_allow_html=True)

    with st.form("add_item_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Item Name*", placeholder="e.g. Wireless Mouse")
        sku = c2.text_input("SKU", placeholder="e.g. SKU-1023")
        category = c1.text_input("Category", placeholder="e.g. Electronics")
        supplier = c2.text_input("Supplier", placeholder="e.g. Acme Distributors")
        quantity = c1.number_input("Quantity", min_value=0, value=0)
        unit_price = c2.number_input("Unit Price (₹)", min_value=0.0, value=0.0, step=1.0)
        reorder_level = c1.number_input("Reorder Level", min_value=0, value=5,
                                         help="You'll be flagged when stock falls to or below this number.")
        submitted = st.form_submit_button("Add to Inventory", type="primary", use_container_width=True)

        if submitted:
            if not name:
                st.error("Item name is required.")
            else:
                add_item(user["id"], name, sku, category, int(quantity), float(unit_price),
                          int(reorder_level), supplier)
                st.success(f"'{name}' added to inventory.")


# ---------------------------------------------------------------------------
# REPORTS PAGE
# ---------------------------------------------------------------------------
def render_reports(user):
    st.markdown('<div class="page-title">Reports</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">A closer look at value and stock distribution.</div>', unsafe_allow_html=True)

    items = get_items(user["id"])
    if not items:
        st.info("Add some inventory items to see reports here.")
        return

    df = pd.DataFrame(items)
    df["value"] = df["quantity"] * df["unit_price"]
    df["cat_clean"] = df["category"].replace("", "Uncategorized")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Value by category (₹)")
        st.bar_chart(df.groupby("cat_clean")["value"].sum())
    with c2:
        st.subheader("Units by category")
        st.bar_chart(df.groupby("cat_clean")["quantity"].sum())

    st.subheader("Top items by value")
    top = df.sort_values("value", ascending=False)[["name", "quantity", "unit_price", "value"]].head(10)
    top.columns = ["Item", "Qty", "Unit Price (₹)", "Total Value (₹)"]
    st.dataframe(top, hide_index=True, use_container_width=True)


# ---------------------------------------------------------------------------
# ROUTER
# ---------------------------------------------------------------------------
if st.session_state.user is None:
    render_auth()
else:
    render_sidebar(st.session_state.user)
    nav = st.session_state.nav
    if nav == "Dashboard":
        render_dashboard(st.session_state.user)
    elif nav == "Inventory":
        render_inventory(st.session_state.user)
    elif nav == "Add Item":
        render_add_item(st.session_state.user)
    elif nav == "Reports":
        render_reports(st.session_state.user)
