from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document  
from dotenv import load_dotenv
import transformers

load_dotenv()
transformers.logging.set_verbosity_error()

# Create LangChain documents
doc1 = Document(
    page_content="Virat Kohli is one of the most successful and consistent batsmen in IPL history. Known for his aggressive batting style and fitness, he has led the Royal Challengers Bangalore in multiple seasons.",
    metadata={"team": "Royal Challengers Bangalore"}
)

doc2 = Document(
    page_content="Rohit Sharma is the most successful captain in IPL history, leading Mumbai Indians to five titles. He's known for his calm demeanor and ability to play big innings under pressure.",
    metadata={"team": "Mumbai Indians"}
)

doc3 = Document(
    page_content="MS Dhoni, famously known as Captain Cool, has led Chennai Super Kings to multiple IPL titles. His finishing skills, wicketkeeping, and leadership are legendary.",
    metadata={"team": "Chennai Super Kings"}
)

doc4 = Document(
    page_content="Jasprit Bumrah is considered one of the best fast bowlers in T20 cricket. Playing for Mumbai Indians, he is known for his yorkers and death-over expertise.",
    metadata={"team": "Mumbai Indians"}
)

doc5 = Document(
    page_content="Ravindra Jadeja is a dynamic all-rounder who contributes with both bat and ball. Representing Chennai Super Kings, his quick fielding and match-winning performances make him a key player.",
    metadata={"team": "Chennai Super Kings"}
)

docs = [doc1, doc2, doc3, doc4, doc5]

# HuggingFace embedding
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Create vector store
vector_store = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory="chroma_db",
    collection_name="sample"
)

# ------------------------------------------------------------------------------------

## View Documents
# res = vector_store.get(include=["embeddings", "documents", "metadatas"])
# print(res)

# ------------------------------------------------------------------------------------

## Search Documents
# results = vector_store.similarity_search("Who among these are a bowler?", k=2)

# for res in results:
#     print("----")
#     print(res.page_content)

# ------------------------------------------------------------------------------------

## Search with similarity score
# results = vector_store.similarity_search_with_score("Who among these are a bowler?", k=2)
# print(results)

# ------------------------------------------------------------------------------------

# ## Meta-data filtering
# results = vector_store.similarity_search_with_score(
#     query="",
#     filter={"team":"Chennai Super Kings"}
# )

# print(results)

# ------------------------------------------------------------------------------------

# # Update documents
# q = Document(
#     page_content="Virat kohli",
#     metadata={"team":"RCB"}
# )

# vector_store.update_document(document_id="ea3857ed-d95c-4c49-a5ea-dd07180d35fb", document=q)

# ------------------------------------------------------------------------------------

# # View Documents
# res = vector_store.get(include=["embeddings", "documents", "metadatas"])
# print(res)

# ------------------------------------------------------------------------------------

# Delete documents
# vector_store.delete(ids=["ea3857ed-d95c-4c49-a5ea-dd07180d35fb"])

# ------------------------------------------------------------------------------------

# # # View Documents
# res = vector_store.get(include=["embeddings", "documents", "metadatas"])
# print(res)

# ------------------------------------------------------------------------------------