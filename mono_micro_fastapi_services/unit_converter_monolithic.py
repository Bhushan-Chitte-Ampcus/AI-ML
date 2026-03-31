from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message" : "Unit Converter API"}

# @app.get("/temp")
# def temp_converter(val : float, from_unit : str, to_unit : str):
#     if from_unit == "c" and to_unit == "f":
#         return val * (9 / 5) + 32
#     elif from_unit == "f" and to_unit == "c":
#         return (val - 32) * (5 / 9)

#     if from_unit == "f" and to_unit == "k":
#         return (val - 32) * (5 / 9) + 273.15
#     elif from_unit == "k" and to_unit == "f":
#         return (val - 273.15) * (9/5) + 32
    
#     if from_unit == "c" and to_unit == "k":
#         return val + 273.15
#     elif from_unit == "k" and to_unit == "c":
#         return val - 273.15


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
    

def convert_length(val, from_unit, to_unit):
    units = {
        'm' : 1,
        'km' : 1000,
        'mile' : 1609.34
    }

    meters = val * units[from_unit]
    return meters / units[to_unit]


def convert_weight(val, from_unit, to_unit):
    units = {
        "kg" : 1,
        "pounds" : 0.453592
    }

    kg = val * units[from_unit]
    return kg / units[to_unit]


@app.get("/convert")
def convert(val: float, from_unit: str, to_unit: str):
    if from_unit in ["C", "F", "K"]:
        result = convert_temp(val, from_unit, to_unit)
        category = "temperature"

    elif from_unit in ["m", "km", "mile"]:
        result = convert_length(val, from_unit, to_unit)
        category = "length"

    elif from_unit in ["kg", "pound"]:
        result = convert_weight(val, from_unit, to_unit)
        category = "weight"

    else:
        return {"error" : "Invalid Operation"}

    return {
        "category" : category,
        "converted_value" : result
    }