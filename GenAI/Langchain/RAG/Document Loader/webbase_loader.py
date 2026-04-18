from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader(
    "https://en.wikipedia.org/wiki/Artificial_intelligence#Reasoning_and_problem-solving"
)

docs = loader.load()

print(len(docs))
print(docs[0].page_content)