from Langchain.Structured_output.pydantic_example import BaseModel, EmailStr, Field
from typing import Optional

# # ------------------------------------------------

# class Student(BaseModel):
#     name : str

# new_student = {"name" : "john"}

# student = Student(**new_student)

# print(student)
# print(type(student))

# ------------------------------------------------

class Student(BaseModel):
    name : str = "john"
    age : Optional[int] = None 
    email : EmailStr
    cgpa : float = Field(gt=0, lt=10, default=5, description="A decimal value representing the cgpa of the student")

new_student = {"age":22, "email":"abc@gmail.com", "cgpa":8.65}

student = Student(**new_student)

print(student)
print(type(student))

student_dict = dict(student)
print(student_dict)

student_json = student.model_dump_json()
print(student_json)

# ------------------------------------------------