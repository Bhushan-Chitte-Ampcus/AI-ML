import os
from dotenv import load_dotenv
import requests
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool
from langchain.agents import create_agent

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

search_tool = DuckDuckGoSearchRun()

@tool
def get_weather_data(city: str) -> str:
    """Fetches current weather data for a given city."""
    url = f"https://api.weatherstack.com/current?access_key={WEATHER_API_KEY}&query={city}"
    response = requests.get(url)
    data = response.json()

    if "current" in data:
        current = data["current"]
        location = data.get("location", {})
        return (
            f"City: {location.get('name')}, "
            f"Country: {location.get('country')}, "
            f"Temperature: {current.get('temperature')}°C, "
            f"Weather: {current.get('weather_descriptions', ['N/A'])[0]}, "
            f"Humidity: {current.get('humidity')}%, "
            f"Wind Speed: {current.get('wind_speed')} km/h"
        )
    return f"Could not fetch weather for '{city}'. Response: {data}"


llm_endpoint = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="text-generation",
    huggingfacehub_api_token=HF_TOKEN,
    temperature=0.5,
    max_new_tokens=512
)

llm = ChatHuggingFace(llm=llm_endpoint)
tools = [search_tool, get_weather_data]

agent = create_agent(
    model=llm,
    tools=tools,
)

response = agent.invoke({
    "messages": [{"role": "user", "content": "Find the capital of Maharashtra, then find its current weather condition."}]
})

print("\nFinal Answer:\n")
print(response["messages"][-1].content)
# print(response)