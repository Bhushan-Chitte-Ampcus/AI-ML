from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn


add_app= FastAPI( title="Add API",description="A simple API to perform addition")
subtract_app= FastAPI( title="Subtract API",description="A simple API to perform subtraction")
multiply_app= FastAPI( title="Multiply API",description="A simple API to perform multiplication")
divide_app= FastAPI( title="Divide API",description="A simple API to perform division")


class Item(BaseModel):
    a : float
    b : float

@add_app.post("/add")
def add(item: Item):
    return {"result": item.a + item.b}

@subtract_app.post("/subtract")
def subtract(item: Item):
    return {"result": item.a - item.b}  

@multiply_app.post("/multiply")
def multiply(item: Item):
    return {"result": item.a * item.b}  

@divide_app.post("/divide")
def divide(item: Item):
    if item.b == 0:
        raise HTTPException(status_code=400, detail="Division by zero is not allowed")
    return {"result": item.a / item.b}  



def run_add():
    uvicorn.run(add_app, host="127.0.0.1", port=8000)

def run_subtract():
    uvicorn.run(subtract_app, host="127.0.0.1", port=8001)

def run_multiply():
    uvicorn.run(multiply_app, host="127.0.0.1", port=8002)

def run_divide():
    uvicorn.run(divide_app, host="127.0.0.1", port=8003)


if __name__ == "__main__":
    import threading
    threads = [
        threading.Thread(target=run_add),
        threading.Thread(target=run_subtract),
        threading.Thread(target=run_multiply),
        threading.Thread(target=run_divide)         
    ]
    for thread in threads:
        thread.start()

    import time
    
    # while True:
    #     time.sleep(10)