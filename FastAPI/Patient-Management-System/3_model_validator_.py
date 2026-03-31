from pydantic import BaseModel, EmailStr, AnyUrl, Field, field_validator, model_validator
from typing import List, Dict, Optional, Annotated

class Patient(BaseModel):
    name : str
    email : EmailStr
    age : int
    weight : float
    married : bool
    allergies : List[str]
    contact_details : Dict[str, str]

    @model_validator(mode="after")
    def validate_emergency_contact(cls, model):
        if model.age > 60 and "emergency" not in model.contact_details:
            raise ValueError("Patient older than 60 must have an emergency contact")
        return model

patient_info = {
    "name" : "john",
    "email" : "abc@hdfc.com",
    "age" : 90,
    "weight" : 53.3,
    "married" : True,
    "allergies" : ["pollen", "dust"],
    "contact_details" : {
        "phone" : "1234567890",
        "emergency" : "1212121212"
    }
}

p1 = Patient(**patient_info)

def insert_detail(patient: Patient):
    print(patient)
    print("Data Inserted...")

insert_detail(p1)
