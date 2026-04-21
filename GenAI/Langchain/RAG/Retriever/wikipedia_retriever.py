from langchain_community.retrievers import WikipediaRetriever

# initialize the retriever
retriever = WikipediaRetriever(
    top_k_results=2,
    lang="en"
)

# define query
query = "the geopolitical history of india and pakistan from the perspective of a chinese"

# get relevant wikipedia documents
docs = retriever.invoke(query)

# print retrieved content
for i, doc in enumerate(docs):
    print(f"\n--- Result {i+1} ---")
    print(f"Content:\n{doc.page_content}...")
    