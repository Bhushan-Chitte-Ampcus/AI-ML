import httpx
from db import get_conn

PRODUCT_URL = "http://localhost:8001"

def get_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, balance FROM users WHERE id=%s", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row

def get_order(order_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, total, status FROM orders WHERE id=%s", (order_id,))
    records = cur.fetchone()
    conn.close()
    return records

def create_order(user_id, product_id, qty, price):
    conn = get_conn()
    cur = conn.cursor()
    try:
        total = qty * price

        cur.execute("INSERT INTO orders (user_id, total, status) VALUES (%s, %s, 'pending') RETURNING id",
                    (user_id, total))
        order_id = cur.fetchone()[0]

        cur.execute("""INSERT INTO order_items (order_id, product_id, quantity, price)
                       VALUES (%s, %s, %s, %s)""",
                    (order_id, product_id, qty, price))

        cur.execute("UPDATE users SET balance = balance - %s WHERE id=%s", (total, user_id))
        cur.execute("UPDATE orders SET status='completed' WHERE id=%s", (order_id,))
        
        conn.commit()
        return order_id
    except:
        conn.rollback()
        return None
    finally:
        conn.close()