from fastapi import FastAPI

# ------------------------------------------------------------------------------------------

temp = FastAPI(title="Temperature Service")

def convert_temp(val, from_unit, to_unit):
    if from_unit == "C":
        c = val
    elif from_unit == "F":
        c = (val - 32) * (5 / 9)
    elif from_unit == "K":
        c = val - 273.15

    if to_unit == "C":
        return c
    elif to_unit == "F":
        return (c * 9/5) + 32
    elif to_unit == "K":
        return c + 273.15


@temp.get("/convert")
def convert(val: float, from_unit: str, to_unit: str):
    result = convert_temp(val, from_unit, to_unit)

    return {
        "category" : "temperature",
        "converted_value" : result
    }

# python -m uvicorn micro:temp --port 8001 --reload
# http://localhost:8001/convert?val=100&from_unit=C&to_unit=F

# ------------------------------------------------------------------------------------------

length = FastAPI(title="Length Service")

def convert_length(val, from_unit, to_unit):
    units = {
        'm' : 1,
        'km' : 1000,
        'mile' : 1609.34
    }

    meters = val * units[from_unit]
    return meters / units[to_unit]


@length.get("/convert")
def convert(val: float, from_unit: str, to_unit: str):
    result = convert_length(val, from_unit, to_unit)

    return {
        "category" : "length",
        "converted_value" : result
    }

# python -m micro:length --port 8002 --reload
# http://localhost:8002/convert?val=1&from_unit=km&to_unit=m

# ------------------------------------------------------------------------------------------

weight = FastAPI(title="Weight Service")

def convert_weight(val, from_unit, to_unit):
    units = {
        "kg" : 1,
        "pounds" : 0.453592
    }

    kg = val * units[from_unit]
    return kg / units[to_unit]


@weight.get("/convert")
def convert(val: float, from_unit: str, to_unit: str):
    result = convert_weight(val, from_unit, to_unit)

    return {
        "category" : "weight",
        "converted_value" : result
    }

# python -m uvicorn micro:weight --port 8003 --reload
# http://localhost:8003/convert?val=10&from_unit=kg&to_unit=pounds

# ------------------------------------------------------------------------------------------