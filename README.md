# StockPilot — Inventory Management (Streamlit)

A Python/Streamlit inventory management app with a sidebar-driven dashboard
layout, teal & slate color scheme, and spreadsheet-style inline editing.

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

## What's included

- **Auth screen** — simple centered Log In / Create Account tabs (no marketing
  landing page), accounts stored in a local SQLite DB (`invease.db`,
  auto-created on first run), passwords hashed (demo-grade, not production security)
- **Sidebar navigation** — Dashboard, Inventory, Add Item, Reports, Log Out
- **Dashboard** — KPI metrics (items, units, low stock, inventory value), a
  stock-by-category bar chart, and a "needs attention" low-stock table
- **Inventory** — search, category filter, and direct **inline editing** in a
  spreadsheet-style table (`st.data_editor`) with a Save Changes button, bulk
  delete by ID, and CSV export
- **Add Item** — form to add new items (name, SKU, category, supplier,
  quantity, price, reorder level)
- **Reports** — value-by-category and units-by-category charts, top items by value

## Deploying

Push `app.py`, `db.py`, and `requirements.txt` to a GitHub repo and deploy on
[Streamlit Community Cloud](https://streamlit.io/cloud) with `app.py` as the
entry point.

## Files

- `app.py` — UI, navigation, and page rendering (**run this file**)
- `db.py` — SQLite schema + CRUD helpers, imported by app.py (not run directly)
- `requirements.txt` — Python dependencies
