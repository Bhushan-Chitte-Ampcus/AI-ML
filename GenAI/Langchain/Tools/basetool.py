from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel

class MultiplyInput(BaseModel):
    a: int
    b: int

class MultiplyTool(BaseTool):
    name: str = "multiply"
    description: str = "multiply two numbers"
    args_schema: Type[BaseModel] = MultiplyInput

    def _run(self, a: int, b: int) -> int:
        return a * b
    
multiply_tool = MultiplyTool()
result = multiply_tool.invoke({"a":3, "b":5})

print(result)
print(multiply_tool.name)
print(multiply_tool.description)
print(multiply_tool.args)