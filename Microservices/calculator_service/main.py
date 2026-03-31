from fastapi import FastAPI, HTTPException

app = FastAPI(title="Calculator Services")

history = []

def log(op, a, b, result):
    history.append({
        "operation": op,
        "a": a,
        "b": b,
        "result": result
    })

@app.get("/add")
def add(a: float, b: float):
    result = a + b
    log("addition", a, b, result)
    return {"operation": "addition", "result": result}

@app.get("/sub")
def sub(a : float, b : float):
    result = a - b
    log("subtraction", a, b, result)
    return {"operation": "subtraction", "result": result}

@app.get("/mul")
def mul(a: float, b : float):
    result = a * b
    log("multiplication", a, b, result)
    return {"operation": "multiplication", "result": result}

@app.get("/div")
def div(a : float, b : float):
    if b == 0:
        raise HTTPException(status_code=400, detail="division by zero")
    result = a / b
    log("division", a, b, result)
    return {"operation": "division", "result": result}

@app.get("/history")
def get_history():
    return history

# http://127.0.0.1:8001/div?a=5&b=10