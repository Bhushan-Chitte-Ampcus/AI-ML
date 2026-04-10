from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# chat template
chat_template = ChatPromptTemplate([
    ("system", "You are a helpful customer support agent"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{query}")
])

# load history
chat_history = []

with open("./chat_history.txt") as f:
    chat_history.extend(f.readlines())

print("-"*50)
print(chat_history)

prompt = chat_template.invoke({"chat_history":chat_history, "query":"where is ny refund"})
print("-"*50)
print(prompt)
print("-"*50)

