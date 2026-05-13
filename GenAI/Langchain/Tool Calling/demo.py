from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

# Create tool
@tool
def multiply(a: int, b: int) -> int:
    """Multiplies two numbers together."""
    return a * b

# Initialize LLM
llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="text-generation"
)

# Create Chat model and bind tools
model = ChatHuggingFace(llm=llm)
llm_with_tools = model.bind_tools([multiply])

# Test tool calling
# Example: Call the model with a request that requires the multiply tool

# message = HumanMessage(content="hi how are you")
query = HumanMessage(content="can you multiply 3 and 400 for me?")
messages = [query]

result = llm_with_tools.invoke(messages)
messages.append(result)

tool_result = multiply.invoke(result.tool_calls[0])
messages.append(tool_result)

# print(messages)
print(llm_with_tools.invoke(messages).content)