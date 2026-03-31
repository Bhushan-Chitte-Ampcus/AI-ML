from pydantic import BaseModel

class Address(BaseModel):
    city : str
    state : str
    pin : str

class Patient(BaseModel):
    name : str
    gender : str
    age : int
    address : Address

address_info = {
    "city" : "Nashik",
    "state" : "Maharashtra",
    "pin" : "422003"
}

add = Address(**address_info)

patient_info = {
    "name" : "John",
    "gender" : "male",
    "age" : 45,
    "address" : add
}

p1 = Patient(**patient_info)

# ------------------------------------------
print("-"*50)
temp1 = p1.model_dump()
print(temp1)
print(type(temp1))
# ------------------------------------------
print("-"*50)
temp1 = p1.model_dump(include=["name", "age"])
print(temp1)
print(type(temp1))
# ------------------------------------------
print("-"*50)
temp1 = p1.model_dump(exclude=["name", "age"])
print(temp1)
print(type(temp1))
# ------------------------------------------
print("-"*50)
temp1 = p1.model_dump(exclude={"address": ["state"]})
print(temp1)
print(type(temp1))
# ------------------------------------------
print("-"*50)
temp2 = p1.model_dump_json()
print(temp2)
print(type(temp2))
print("-"*50)
# ------------------------------------------
