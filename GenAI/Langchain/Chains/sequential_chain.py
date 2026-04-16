from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import transformers

load_dotenv()
transformers.logging.set_verbosity_error()

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="text-generation"
)

model = ChatHuggingFace(
    llm = llm
)

parser = StrOutputParser()

prompt1 = PromptTemplate(
    template="Generate a detailed report on {topic}",
    input_variables=["topic"]
)

prompt2 = PromptTemplate(
    template="Generate a 2 pointer summary from the following text: {text}",
    input_variables=["text"]
)

chain = prompt1 | model | parser | prompt2 | model | parser

result = chain.invoke({"topic": "unemployment in India"})
print(result)

chain.get_graph().print_ascii()
