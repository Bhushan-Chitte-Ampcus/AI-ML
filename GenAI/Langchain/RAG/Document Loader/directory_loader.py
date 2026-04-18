from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_community.document_loaders.unstructured import UnstructuredFileLoader

loader = DirectoryLoader(
    path="./documents",
    glob="**/*",
    loader_cls=UnstructuredFileLoader,
    loader_kwargs={"encoding": "utf-8"}
)

docs = loader.load()

print(len(docs))