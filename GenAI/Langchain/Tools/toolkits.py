from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """add two numbers"""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """multiply two numbers"""
    return a * b

class MathToolkit:
    def get_tools(self):
        return [add, multiply]
    
toolkit = MathToolkit()
tools = toolkit.get_tools()

for tool in tools:
    print(f"{tool.name} => {tool.description}")