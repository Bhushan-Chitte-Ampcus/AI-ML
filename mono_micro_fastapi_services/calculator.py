from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message" : "Calculator Using FastAPI"}

@app.get("/add")
def add(a : float, b : float):
    return a + b

@app.get("/sub")
def sub(a : float, b : float):
    return a - b

@app.get("/mul")
def mul(a: float, b : float):
    return a * b

@app.get("/div")
def div(a : float, b : float):
    if b == 0:
        return {"error" : "cannot divide by zero"}
    return a / b
