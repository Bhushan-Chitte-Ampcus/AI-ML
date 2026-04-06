import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM

print("Loading dataset...")

dataset = load_dataset("blended_skill_talk")

dialogs = []

for item in dataset["train"]:

    conversation = ""

    if item["previous_utterance"]:
        conversation += " ".join(item["previous_utterance"]) + " "

    if item["guided_messages"]:
        conversation += " ".join(item["guided_messages"]) + " "

    if item["free_messages"]:
        conversation += " ".join(item["free_messages"])

    dialogs.append(conversation)

print("Dataset loaded:", len(dialogs))

print("Loading model...")

model_name = "distilgpt2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

tokenizer.pad_token = tokenizer.eos_token

print("Chatbot ready! Type 'quit' to stop.\n")

chat_history = ""

while True:

    user_input = input("User: ")

    if user_input.strip().lower() == "quit":
        break

    chat_history += user_input + tokenizer.eos_token

    inputs = tokenizer(chat_history, return_tensors="pt")

    inputs = tokenizer(chat_history, return_tensors="pt")

    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]

    output = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_length=120,
        temperature=0.7,
        do_sample=True,
        top_k=40,
        top_p=0.9,
        repetition_penalty=1.2,
        pad_token_id=tokenizer.eos_token_id
    )

    response = tokenizer.decode(
        output[:, input_ids.shape[-1]:][0],
        skip_special_tokens=True
    )

    print("Bot:", response)

    chat_history += response + tokenizer.eos_token