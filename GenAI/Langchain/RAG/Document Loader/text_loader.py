from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import transformers

load_dotenv()
transformers.logging.set_verbosity_error()

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct", 
    task="text-generation",
    huggingfacehub_api_token=os.getenv("HF_TOKEN")
)

model = ChatHuggingFace(
    llm=llm
)

parser = StrOutputParser()

prompt = PromptTemplate(
    template = "write a short summary for the following poem - \n{poem}",
    input_variables=["poem"]
)

loader = TextLoader("./documents/cricket.txt", encoding="utf-8")
docs = loader.load()

# print(docs)
# print(type(docs))
# print(len(docs))
# print(docs[0].page_content)
# print(docs[0].metadata)

chain = prompt | model | parser
result = chain.invoke({"poem": docs[0].page_content})

print(result)