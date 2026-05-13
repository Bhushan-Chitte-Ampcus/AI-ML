from langchain_community.tools import StructuredTool
from pydantic import BaseModel, Field

class MultiplyInput(BaseModel):
    a : int 
    b : int

def multiply(a: int, b: int) -> int:
    return a * b

multiply_tool = StructuredTool.from_function(
    func=multiply,
    name="multiply",
    description="multiply two numbers",
    args_schema=MultiplyInput
)

result = multiply_tool.invoke({"a":3, "b":5})
print(result)