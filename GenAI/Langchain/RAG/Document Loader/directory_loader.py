from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.unstructured import UnstructuredFileLoader

loader = DirectoryLoader(
    path="./documents",
    glob="**/*",
    loader_cls=UnstructuredFileLoader,
    loader_kwargs={
        "encoding": "utf-8",
        "languages": ["eng"]
    }
)

docs = loader.load()

print(f"Loaded {len(docs)} documents")
print(docs[0].page_content)
print(docs[0].metadata)
