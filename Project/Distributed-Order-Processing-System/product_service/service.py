import psycopg2
from db import get_conn

def get_all_product():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products;")
    records = cur.fetchall()
    conn.close()
    return records

def get_product(product_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, stock, price FROM products WHERE id=%s", (product_id,))
    row = cur.fetchone()
    conn.close()
    return row

def reserve_stock(product_id, qty):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT stock FROM products WHERE id=%s", (product_id,))
        stock = cur.fetchone()[0]

        if stock < qty:
            return False

        cur.execute("UPDATE products SET stock = stock - %s WHERE id=%s", (qty, product_id))
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()

def release_stock(product_id, qty):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE products SET stock = stock + %s WHERE id=%s", (qty, product_id))
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()