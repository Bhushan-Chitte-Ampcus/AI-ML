from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.tools import tool, InjectedToolArg
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import requests
from typing import Annotated

load_dotenv()

@tool
def get_conversion_factor(base_currency: str, target_currency: str) -> float:
    """This function fetches the currency conversion factor between a given base currency and a target currency."""
    url = f"https://v6.exchangerate-api.com/v6/9476306fac48d6835253357d/pair/{base_currency}/{target_currency}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    return float(data["conversion_rate"])

@tool
def convert(base_currency_value: int, conversion_rate: Annotated[float, InjectedToolArg]) -> float:
    """This function converts a given amount of base currency to the target currency using the conversion rate."""
    return base_currency_value * conversion_rate

# rate = get_conversion_factor.invoke({"base_currency": "USD", "target_currency": "INR"})
# print(f"USD -> INR conversion factor: {rate}")

# converted_value = convert.invoke({"base_currency_value": 1, "conversion_rate": rate})
# print(f"1 USD = {converted_value} INR")

# tool binding
llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="text-generation"
)

model = ChatHuggingFace(llm=llm)
llm_with_tools = model.bind_tools([get_conversion_factor, convert])

messages = [HumanMessage("What is the conversion factor between USD and INR, and based on that can you convert 10 usd to inr")]

ai_message = llm_with_tools.invoke(messages)
messages.append(ai_message)
# print(ai_message.tool_calls)


for tool_call in ai_message.tool_calls:
    if tool_call["name"] == "get_conversion_factor":
        tool_message1 = get_conversion_factor.invoke(tool_call)
        conversion_rate = float(tool_message1.content)
        messages.append(tool_message1)
    elif tool_call["name"] == "convert":
        tool_call["args"]["conversion_rate"] = conversion_rate
        tool_message2 = convert.invoke(tool_call)
        messages.append(tool_message2)

# print(messages)

llm_response = llm_with_tools.invoke(messages).content
print(llm_response)
