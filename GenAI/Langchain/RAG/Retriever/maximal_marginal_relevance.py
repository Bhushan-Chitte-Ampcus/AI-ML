from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import transformers

transformers.logging.set_verbosity_error()

docs = [
    Document(page_content="Langchain makes it easy to work with LLMs."),
    Document(page_content="Langchain is used to build LLM based applications"),
    Document(page_content="Chroma is used to store and search document embeddings."),
    Document(page_content="embedding are vector representations of text."),
    Document(page_content="MMR helps you get diverse results when going similarity search."),
    Document(page_content="langchain supports chroma, FAISS, pinecone and more")
]

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},  
    encode_kwargs={'normalize_embeddings': False}
)

vectorstore = FAISS.from_documents(
    documents=docs,
    embedding=embedding_model
)

retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k":3, "lambda_mult":0.5} # lambda_mult = relevance-diversity balance (0 = more diverse, 1 = acts as semantic search)
)

query = "what is langchain?"
results = retriever.invoke(query)

for i, doc in enumerate(results):
    print(f"--- Result {i+1} ---")
    print(doc.page_content)