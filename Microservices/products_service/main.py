from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Product Services")

class Product(BaseModel):
    name: str
    price: float
    description: str
    stock: int

products = []

@app.post("/products")
def create_product(product: Product):
    new_product = {"id": len(products)+1, **product.dict()}
    products.append(new_product)
    return new_product

@app.get("/products")
def get_all_products():
    return products

@app.get("/products/{product_id}")
def get_product_detail(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return {"error": "details not found"}

@app.put("/products/{product_id}")
def update_product_detail(product_id: int, update: Product):
    for i, product in enumerate(products):
        if product["id"] == product_id:
            products[i] = {"id":  product_id, **update.dict()}
            return products[i]
    return {"error": "product not found"}

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    for i, product in enumerate(products):
        if product["id"] == product_id:
            return products.pop(i)
    return {"error": "product not found"}