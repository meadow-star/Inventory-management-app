import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide",
)

PURPLE = "#4b1f6f"
LIGHT_PURPLE = "#f1e7f7"

st.markdown(
    f"""
    <style>
      .stApp {{ background: #ffffff; }}
      h1, h2, h3 {{ color: {PURPLE}; }}
      .block-container {{ padding-top: 2rem; padding-bottom: 3rem; }}
      [data-testid="stMetric"] {{
        background: {LIGHT_PURPLE};
        border: 1px solid #e3d0ee;
        padding: 14px 16px;
        border-radius: 10px;
      }}
      div[data-testid="stDataFrame"] {{ border: 1px solid #e6dcec; border-radius: 10px; }}
      .report-note {{ color: #6d6175; font-size: 0.92rem; }}
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


def inventory_df() -> pd.DataFrame:
    return pd.DataFrame(st.session_state.inventory)


def totals():
    items = st.session_state.inventory
    total_products = len(items)
    total_units = sum(item["quantity"] for item in items)
    total_value = sum(item["quantity"] * item["price"] for item in items)
    low_stock = sum(1 for item in items if item["quantity"] < 10)
    return total_products, total_units, total_value, low_stock


st.title("Inventory Management System")
st.caption("Organize Stock. Process Data. Manage Better.")
st.markdown(
    '<div class="report-note">B.Sc. Artificial Intelligence and Machine Learning | Semester I | Academic Year 2026-2027</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Inventory Operations")
    operation = st.radio(
        "Choose Operation",
        ["Dashboard", "Add Product", "Search Product", "Update Product", "Delete Product", "Low-Stock View"],
    )
    st.divider()
    st.subheader("Project Team")
    st.write("Vanshika - 267111")
    st.write("Asim - 267136")
    st.write("Jonathan - 267108")
    st.caption("Thakur College of Science and Commerce")


if operation == "Dashboard":
    total_products, total_units, total_value, low_stock = totals()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Products", total_products)
    c2.metric("Total Units", total_units)
    c3.metric("Inventory Value", f"₹{total_value:,.0f}")
    c4.metric("Low Stock", low_stock)

    st.subheader("Current Inventory")
    df = inventory_df()
    if df.empty:
        st.info("No products are currently stored in the inventory.")
    else:
        display_df = df.copy()
        display_df["price"] = display_df["price"].map(lambda x: f"₹{x:,.0f}")
        display_df.columns = ["Product", "Category", "Quantity", "Price"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

elif operation == "Add Product":
    st.subheader("Add Product")
    with st.form("add_product_form", clear_on_submit=True):
        name = st.text_input("Product Name")
        category = st.text_input("Category")
        quantity = st.number_input("Quantity", min_value=0, step=1)
        price = st.number_input("Price (₹)", min_value=0.0, step=1.0)
        submitted = st.form_submit_button("Add Product", use_container_width=True)

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
            st.success("Product added successfully!")

elif operation == "Search Product":
    st.subheader("Search Product")
    query = st.text_input("Enter product name or keyword")
    if query.strip():
        results = [
            item
            for item in st.session_state.inventory
            if query.lower() in item["name"].lower()
        ]
        if results:
            df = pd.DataFrame(results)
            df["price"] = df["price"].map(lambda x: f"₹{x:,.0f}")
            df.columns = ["Product", "Category", "Quantity", "Price"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("No matching product found.")

elif operation == "Update Product":
    st.subheader("Update Product")
    if not st.session_state.inventory:
        st.info("There are no products to update.")
    else:
        names = [item["name"] for item in st.session_state.inventory]
        selected = st.selectbox("Select Product", names)
        index = names.index(selected)
        item = st.session_state.inventory[index]

        with st.form("update_product_form"):
            new_qty = st.number_input("New Quantity", min_value=0, value=int(item["quantity"]), step=1)
            new_price = st.number_input("New Price (₹)", min_value=0.0, value=float(item["price"]), step=1.0)
            update = st.form_submit_button("Update Product", use_container_width=True)

        if update:
            st.session_state.inventory[index]["quantity"] = int(new_qty)
            st.session_state.inventory[index]["price"] = float(new_price)
            st.success("Product updated successfully!")

elif operation == "Delete Product":
    st.subheader("Delete Product")
    if not st.session_state.inventory:
        st.info("There are no products to delete.")
    else:
        names = [item["name"] for item in st.session_state.inventory]
        selected = st.selectbox("Select Product", names)
        st.warning(f"This will remove '{selected}' from the current inventory session.")
        if st.button("Delete Product", type="primary", use_container_width=True):
            st.session_state.inventory = [
                item for item in st.session_state.inventory if item["name"] != selected
            ]
            st.success("Product deleted successfully!")
            st.rerun()

elif operation == "Low-Stock View":
    st.subheader("Low-Stock View")
    threshold = st.number_input("Low-stock threshold", min_value=1, value=10, step=1)
    low_items = [
        item for item in st.session_state.inventory if item["quantity"] < threshold
    ]
    if low_items:
        df = pd.DataFrame(low_items)
        df["price"] = df["price"].map(lambda x: f"₹{x:,.0f}")
        df.columns = ["Product", "Category", "Quantity", "Price"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.success("No products are below the selected low-stock threshold.")

st.divider()
st.caption(
    "Academic prototype: inventory data is stored in the current Streamlit session and may reset when the application restarts."
)
