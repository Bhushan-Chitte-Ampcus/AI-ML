from fastapi import FastAPI
from service import *

app = FastAPI(title="Product Services")

@app.get("/products")
def fetch_all():
    return {"product": get_all_product()}

@app.get("/products/{id}")
def fetch(id: int):
    return {"product": get_product(id)}

@app.patch("/products/{id}/reserve")
def reserve(id: int, qty: int):
    if reserve_stock(id, qty):
        return {"reserved": True}
    return {"reserved": False}

@app.patch("/products/{id}/release")
def release(id: int, qty: int):
    release_stock(id, qty)
    return {"message": "Stock released"}

@app.post("/init-data")
def init():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO products (name, stock, price) VALUES ('Laptop', 10, 50000)")
    cur.execute("INSERT INTO products (name, stock, price) VALUES ('Mouse', 20, 500)")
    conn.commit()
    conn.close()
    return {"status": "done"}