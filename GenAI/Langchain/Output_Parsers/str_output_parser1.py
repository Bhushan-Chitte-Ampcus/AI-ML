# from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
# from dotenv import load_dotenv
# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# import transformers

# load_dotenv()

# transformers.logging.set_verbosity_error()

# llm = HuggingFacePipeline.from_model_id(
#     model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
#     task = "text-generation",
#     pipeline_kwargs= dict(
#         temperature = 0.5,
#         max_new_tokens = 100 
#     )
# )

# model = ChatHuggingFace(llm=llm)

# # 1st prompt template -> detailed report
# template1 = PromptTemplate(
#     template="Write a detailed report on {topic}",
#     input_variables=["topic"]
# )

# # 2nd prompt template -> summary of the report
# template2 = PromptTemplate(
#     template="Write a 5 line summary on the following text: {text}",
#     input_variables=["text"]
# )

# parser = StrOutputParser()

# chain = template1 | model | parser | template2 | model | parser

# result = chain.invoke({"topic": "black hole"})
# print(result)


# --------------------------------------------------------------------------------

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import transformers

load_dotenv()

transformers.logging.set_verbosity_error()

llm = HuggingFaceEndpoint(
    repo_id = "Qwen/Qwen2.5-7B-Instruct",
    task = "text-generation"
)

model = ChatHuggingFace(llm=llm)

# 1st prompt template -> detailed report
template1 = PromptTemplate(
    template="Write a detailed report on {topic}",
    input_variables=["topic"]
)

# 2nd prompt template -> summary of the report
template2 = PromptTemplate(
    template="Write a 5 line summary on the following text: {text}",
    input_variables=["text"]
)

parser = StrOutputParser()

chain = template1 | model | parser | template2 | model | parser

result = chain.invoke({"topic": "black hole"})
print(result)