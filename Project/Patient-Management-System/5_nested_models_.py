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

print(p1.name)
print(p1.gender)
print(p1.age)
print(p1.address.city)
print(p1.address.state)
print(p1.address.pin)


# ----------------------- NOTE --------------------------------------------------

# Better organization of related data.
# Reusability : Use vitals in multiple models.
# Readability : Easier for developers and API consumers to understand.
# Validation : Nested models are validated automatically - no extra work needed.

# --------------------------------------------------------------------------------