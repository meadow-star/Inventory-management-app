"""
db.py — SQLite data layer for InvEase (Inventory Management System)
Handles table creation and all CRUD operations for users + inventory items.
"""

import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "invease.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            company TEXT,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            sku TEXT,
            category TEXT,
            quantity INTEGER NOT NULL DEFAULT 0,
            unit_price REAL NOT NULL DEFAULT 0,
            reorder_level INTEGER NOT NULL DEFAULT 5,
            supplier TEXT,
            date_added TEXT NOT NULL,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()


# ---------------- Auth helpers ----------------

def hash_password(password: str) -> str:
    salt = "invease_static_salt"  # simple demo-grade hashing
    return hashlib.sha256((salt + password).encode()).hexdigest()


def register_user(full_name, email, company, password):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (full_name, email, company, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
            (full_name.strip(), email.strip().lower(), company.strip(), hash_password(password),
             datetime.now().isoformat()),
        )
        conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    finally:
        conn.close()


def authenticate_user(email, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None
    if row["password_hash"] == hash_password(password):
        return dict(row)
    return None


def get_user_by_id(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# ---------------- Inventory CRUD ----------------

def add_item(owner_id, name, sku, category, quantity, unit_price, reorder_level, supplier):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO items (owner_id, name, sku, category, quantity, unit_price, reorder_level, supplier, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (owner_id, name.strip(), sku.strip(), category.strip(), quantity, unit_price,
          reorder_level, supplier.strip(), datetime.now().isoformat()))
    conn.commit()
    conn.close()


def update_item(item_id, name, sku, category, quantity, unit_price, reorder_level, supplier):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE items SET name=?, sku=?, category=?, quantity=?, unit_price=?, reorder_level=?, supplier=?
        WHERE id=?
    """, (name.strip(), sku.strip(), category.strip(), quantity, unit_price, reorder_level,
          supplier.strip(), item_id))
    conn.commit()
    conn.close()


def delete_item(item_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


def get_items(owner_id, search="", category_filter="All"):
    conn = get_conn()
    cur = conn.cursor()
    query = "SELECT * FROM items WHERE owner_id = ?"
    params = [owner_id]
    if search:
        query += " AND (name LIKE ? OR sku LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if category_filter and category_filter != "All":
        query += " AND category = ?"
        params.append(category_filter)
    query += " ORDER BY date_added DESC"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_categories(owner_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM items WHERE owner_id = ? AND category != ''", (owner_id,))
    rows = [r["category"] for r in cur.fetchall()]
    conn.close()
    return sorted(rows)


def get_stats(owner_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c, COALESCE(SUM(quantity),0) as q, COALESCE(SUM(quantity*unit_price),0) as v FROM items WHERE owner_id=?", (owner_id,))
    row = cur.fetchone()
    total_items, total_qty, total_value = row["c"], row["q"], row["v"]

    cur.execute("SELECT COUNT(*) as c FROM items WHERE owner_id=? AND quantity <= reorder_level AND quantity > 0", (owner_id,))
    low_stock = cur.fetchone()["c"]

    cur.execute("SELECT COUNT(*) as c FROM items WHERE owner_id=? AND quantity = 0", (owner_id,))
    out_of_stock = cur.fetchone()["c"]

    conn.close()
    return {
        "total_items": total_items,
        "total_quantity": total_qty,
        "total_value": total_value,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
    }
