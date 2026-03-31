from pydantic import BaseModel, EmailStr, AnyUrl, Field, field_validator
from typing import List, Dict, Optional, Annotated

class Patient(BaseModel):
    name : str
    email : EmailStr
    age : int
    weight : float
    married : bool
    allergies : List[str]
    contact_details : Dict[str, str]


    @field_validator("email")
    @classmethod
    def email_validator(cls, value):
        valid_domains = ["hdfc.com", "icici.com"]

        domain_name = value.split("@")[-1]
        
        if domain_name not in valid_domains:
            raise ValueError("Not a valid domain")
        return value

    @field_validator("name")
    @classmethod
    def name_validator(cls, value):
        return value.title()
    
    @field_validator("age", mode="after")  # mode = "after" or "before"
    @classmethod
    def age_validator(cls, value):
        if 0 < value < 100:
            return value
        else:
            raise ValueError("Age should be in between 0 & 100")

patient_info = {
    "name" : "john",
    "email" : "abc@hdfc.com",
    "age" : 30,
    "weight" : 53.3,
    "married" : True,
    "allergies" : ["pollen", "dust"],
    "contact_details" : {
        "phone" : "1234567890"
    }
}

p1 = Patient(**patient_info)

def insert_detail(patient: Patient):
    print(patient)
    print("Data Inserted...")

insert_detail(p1)
