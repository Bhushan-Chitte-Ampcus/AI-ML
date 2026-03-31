from fastapi import FastAPI
import httpx
from service import *
from fastapi import HTTPException

app = FastAPI(title="Order Services")

@app.post("/checkout")
async def checkout(user_id: int, product_id: int, quantity: int):
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404

    async with httpx.AsyncClient() as client:
        product = (await client.get(f"{PRODUCT_URL}/products/{product_id}")).json()["product"]
        price = product[3]


        reserve = (await client.patch(f"{PRODUCT_URL}/products/{product_id}/reserve?qty={quantity}")).json()
        if not reserve["reserved"]:
            return {"error": "Out of stock"}, 409
        
        total = price * quantity
        if user[2] < total:
            await client.patch(f"{PRODUCT_URL}/products/{product_id}/release?qty={quantity}")
            return {"error": "Insufficient balance"}, 422

        order_id = create_order(user_id, product_id, quantity, price)
        return {"order_id": order_id}

@app.get("/users/{user_id}")
def get_user_detail(user_id: int):
    return get_user(user_id)

@app.get("/orders/{order_id}")
def get_order_detail(order_id: int):
    return get_order(order_id)

@app.post("/init-data")
def init():
    conn = get_conn()
    cur = conn.cursor()
    
    users_data = [
        ('Bhushan', 100000),
        ('Shubham', 200000),
        ('Samu', 1500000),
        ('Shruti', 500000)
    ]

    cur.executemany("INSERT INTO users (name, balance) VALUES (%s, %s)", users_data)
    conn.commit()
    conn.close()
    return {"status": "done"}