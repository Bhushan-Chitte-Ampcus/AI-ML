from pydantic import BaseModel, EmailStr, AnyUrl, Field, field_validator, model_validator, computed_field
from typing import List, Dict, Optional, Annotated

class Patient(BaseModel):
    name : str
    email : EmailStr
    age : int
    weight : float # in kg
    height : float # in mtr
    married : bool
    allergies : List[str]
    contact_details : Dict[str, str]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height**2), 2)
        return bmi

patient_info = {
    "name" : "john",
    "email" : "abc@hdfc.com",
    "age" : 90,
    "weight" : 75.2,
    "height" : 1.72,
    "married" : True,
    "allergies" : ["pollen", "dust"],
    "contact_details" : {
        "phone" : "1234567890",
        "emergency" : "1212121212"
    }
}

p1 = Patient(**patient_info)

def insert_detail(patient: Patient):
    # print(patient)
    print("BMI:", patient.bmi)
    print("Data Inserted...")

insert_detail(p1)
