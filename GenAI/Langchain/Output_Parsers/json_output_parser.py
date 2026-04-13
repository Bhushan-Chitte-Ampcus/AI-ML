from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import transformers

load_dotenv()

transformers.logging.set_verbosity_error()

llm = HuggingFaceEndpoint(
    repo_id = "Qwen/Qwen2.5-7B-Instruct",
    task = "text-generation"
)

model = ChatHuggingFace(llm=llm)

parser = JsonOutputParser()

template = PromptTemplate(
    template="Give me the name, age and city of a fictional person \n {format_instruction}",
    input_variables=[],
    partial_variables={"format_instruction": parser.get_format_instructions()}
)

# # ---------------------------------------------------------------------
# prompt = template.format()
# # print(prompt)

# result = model.invoke(prompt)
# # print(result)

# final_result = parser.parse(result.content)
# print(final_result)
# # ---------------------------------------------------------------------

chain = template | model | parser
result = chain.invoke({})

print(result)