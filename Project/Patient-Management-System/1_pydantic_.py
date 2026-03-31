from pydantic import BaseModel, EmailStr, AnyUrl, Field
from typing import List, Dict, Optional, Annotated

class Patient(BaseModel):
    name : Annotated[str, Field(max_length=25, title="Name of the patient", description="Give the name of the patient in less than 25 characters", example=["John", "Jenny"])]
    email : EmailStr
    linkedin_url : AnyUrl
    age : int = Field(gt=0, lt=120)
    weight : Annotated[float, Field(gt=0, strict=True)]
    # married : bool = False  # set default value
    # allergies : Optional[List[str]] = None # set optional field with None
    married : Annotated[bool, Field(default=None, description="Is the patient married or not")] 
    allergies : Annotated[Optional[List[str]], Field(default=None, max_items = 5)]
    contact_details : Dict[str, str]

patient_info = {
    "name" : "john",
    "email" : "abc@gmail.com",
    "linkedin_url" : "http://linkedin.com/1212",
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
