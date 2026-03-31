from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI(title="Patient Data Management")

class Info(BaseModel):
    name : Annotated[str, Field(..., description="Name of the patient")]
    city : Annotated[str, Field(..., description="City where the patient is living")]
    age : Annotated[int, Field(..., gt=0, lt=120, description="Age of the patient")]
    gender : Annotated[Literal["male", "female", "others"], Field(..., description="Gender of the patient")]
    height : Annotated[float, Field(..., gt=0, description="Height of the patient in meters")]
    weight : Annotated[float, Field(..., gt=0, description="Weight of the patient in kgs")]
    # bmi : float
    # verdict : str

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 30:
            return "Normal"
        else:
            return "Obese"
        
class InfoUpdate(BaseModel):
    name : Annotated[Optional[str], Field(default=None)]
    city : Annotated[Optional[str], Field(default=None)]
    age : Annotated[Optional[int], Field(default=None, gt=0)]
    gender : Annotated[Optional[Literal["male", "female", "others"]], Field(default=None)]
    height : Annotated[Optional[float], Field(default=None, gt=0)]
    weight : Annotated[Optional[float], Field(default=None, gt=0)]

def load_data():
    with open("./data.json", "r") as f:
        data = json.load(f)
    return data

def save_data(data):
    with open("./data.json", "w") as f:
        json.dump(data, f, indent=2)


@app.get("/")
def root():
    return {"message": "home"}

@app.get("/about")
def about():
    return {"message": "patient data management service"}

@app.get("/view")
def view():
    data = load_data()
    return {"all records" : data}

@app.get("/view/{patient_id}")
def patient_view(patient_id: str = Path(..., description="ID of the patient in the database", example="P001")):
    data = load_data()
    
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient Not Found")

@app.get("/sort")
def sort_patients(sort_by : str = Query(..., description="sort on the basis of height, weight or bmi"), order : str = Query("asc", description="sort in asc or desc order")):
    valid_fields = ["height", "weight", "bmi"]
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid field select from {valid_fields}")
    
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order select between asc & desc")
    
    data = load_data()

    sort_order = True if order=="desc" else False
    sorted_data = sorted(data.values(), key = lambda x : x.get(sort_by, 0), reverse=sort_order)
    return sorted_data

@app.post("/create")
def create(info : Info):
    data = load_data()

    new_id = f"P{len(data) + 1:03d}"
    # new_record = {"id" : new_id, **info.dict()}
    data[new_id] = info.model_dump()

    save_data(data)

    return JSONResponse(status_code=201, content={"message": "patient created successfully..."})

@app.put("/update/{patient_id}")
def update(patient_id: str, info_update: InfoUpdate):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # update_record = {"id": patient_id, **info_update.dict()}
    # data[patient_id] = update_record

    existing_patient_info = data[patient_id]
    updated_patient_info = info_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    info_pydantic_obj = Info(**existing_patient_info)
    existing_patient_info = info_pydantic_obj.model_dump()

    data[patient_id] = existing_patient_info

    save_data(data)

    return JSONResponse(status_code=200, content={"message": "patient updated..."})
    
@app.delete("/delete/{patient_id}")
def delete(patient_id: str):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="patient not found")
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={"message": "patient deleted..."})
