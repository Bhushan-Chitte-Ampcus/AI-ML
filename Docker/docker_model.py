from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:12434/engines/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="ai/smollm2:360M-Q4_K_M",
    messages=[
        {
            "role": "user",
            "content": "What is Docker? Explain in 3 points."
        }
    ],
    temperature=0.2,
    max_tokens=150
)

print(response.choices[0].message.content)