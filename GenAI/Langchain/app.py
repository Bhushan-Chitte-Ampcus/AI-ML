from langchain_huggingface import HuggingFaceEmbeddings, ChatHuggingFace, HuggingFacePipeline
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import transformers
import os
import time

# RAG chatbot with a cricket knowledge base.

transformers.logging.set_verbosity_error()

load_dotenv()

os.environ["HF_HOME"] = "D:/huggingface_cache"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Embedding Model
embedding = HuggingFaceEmbeddings(
    # model_name="BAAI/bge-small-en"
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Local LLM
llm_pipeline = HuggingFacePipeline.from_model_id(
    model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    task="text-generation",
    model_kwargs={
        "torch_dtype": "auto",
        "device_map": "auto"
    },
    pipeline_kwargs=dict(
        temperature=0.5,
        max_new_tokens=80
    )
)

llm = ChatHuggingFace(llm=llm_pipeline)
llm.invoke("Hello")

documents = [
    "Virat Kohli is an Indian cricketer known for his aggressive batting and leadership. He has captained India in all formats and is one of the fastest players to score 10,000 ODI runs.",
    
    "MS Dhoni is a former Indian captain famous for his calm demeanor and finishing skills. He led India to victories in the 2007 T20 World Cup, 2011 ODI World Cup, and 2013 Champions Trophy.",
    
    "Sachin Tendulkar, also known as the 'God of Cricket', holds many batting records including 100 international centuries and over 34,000 international runs.",
    
    "Rohit Sharma is known for his elegant batting and record-breaking double centuries in ODI cricket. He has scored three double hundreds in ODIs, the most by any player.",
    
    "Jasprit Bumrah is an Indian fast bowler known for his unorthodox bowling action and deadly yorkers, especially in the death overs.",
    
    "Kapil Dev was the captain of the Indian cricket team that won the 1983 Cricket World Cup, India's first World Cup victory.",
    
    "Rahul Dravid, known as 'The Wall', was famous for his solid defensive technique and consistency in Test cricket.",
    
    "Anil Kumble is one of India's greatest spin bowlers and has taken over 600 wickets in Test cricket.",
    
    "Sourav Ganguly, also called 'Dada', transformed the Indian team with aggressive leadership and built a strong overseas-performing team.",
    
    "Hardik Pandya is an Indian all-rounder known for explosive batting and fast bowling abilities in limited-overs cricket.",
    
    "Ravindra Jadeja is one of the best all-rounders in the world, contributing with spin bowling, batting, and exceptional fielding.",
    
    "Shikhar Dhawan is an aggressive opening batsman known for strong performances in ICC tournaments.",
    
    "KL Rahul is a versatile Indian batsman who can play in multiple positions and has scored centuries in all formats.",
    
    "Yuvraj Singh played a crucial role in India's 2007 T20 World Cup and 2011 ODI World Cup victories and famously hit six sixes in an over in T20 cricket.",
    
    "Mohammad Shami is an Indian fast bowler known for seam movement and his ability to take wickets in all formats.",
    
    "Sunil Gavaskar was one of the greatest opening batsmen in cricket history and the first player to score 10,000 runs in Test cricket.",
    
    "Virender Sehwag was known for his explosive batting style and is one of the few players to score two triple centuries in Test cricket.",
    
    "Bhuvneshwar Kumar is a swing bowler known for his ability to move the ball both ways, especially in early overs.",
    
    "Rishabh Pant is an attacking wicketkeeper-batsman known for fearless stroke play and match-winning innings.",
    
    "India is one of the most successful cricket teams in the world, winning multiple ICC trophies including the 1983 and 2011 ODI World Cups."
]

doc_embeddings = embedding.embed_documents(documents)

print("\nType 'q' to quit\n")

while True:

    query = input("Ask: ")

    if query.lower() == "q":
        break

    start_time = time.time()
    
    query_embedding = embedding.embed_query(query)

    scores = cosine_similarity([query_embedding], doc_embeddings)[0]

    index = scores.argmax()
    score = scores[index]

    if score < 0.40:
        # General question
        response = llm.invoke(query)
    else:
        # Use RAG
        retrieved_doc = documents[index]

        prompt = f""" 
        You are a helpful assistant. Use the context below to answer the question.
        Context: {retrieved_doc} 
        Question: {query} 
        Answer in a clear and informative way. """

        response = llm.invoke(prompt)


    print("-"*50)
    print(response.content.split("<|assistant|>")[-1].strip())
    print(f"Time Required: {time.time() - start_time}")
    print("-"*50)

