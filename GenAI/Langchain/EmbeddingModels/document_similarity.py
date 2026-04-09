from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import transformers

transformers.logging.set_verbosity_error()

load_dotenv()

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

documents = [
    "Virat Kohli is an Indian cricketer known for his aggressive batting and leadership.",
    "MS Dhoni is a former Indian captain famous for his calm demeanor and finishing skills.",
    "Sachin Tendulkar, also known as the 'God of Cricket', holds many batting records.",
    "Rohit Sharma is known for his elegant batting and record-breaking double centuries.",
    "Jasprit Bumrah is an Indian fast bowler known for his unorthodox action and yorkers."
]

# Embed documents only once
doc_embeddings = embedding.embed_documents(documents)

print("\nType 'q' to quit the program\n")

while True:
    query = input("Ask: ")

    # Exit condition
    if query.lower() == "q":
        print("Exiting program...")
        break

    query_embedding = embedding.embed_query(query)

    scores = cosine_similarity([query_embedding], doc_embeddings)[0]

    index = scores.argmax()
    score = scores[index]

    print("-" * 50)
    print(f"Result: {documents[index]}")
    print(f"Similarity score: {score}")
    print("-" * 50)