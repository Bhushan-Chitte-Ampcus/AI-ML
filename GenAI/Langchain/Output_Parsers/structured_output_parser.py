from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StructuredOutputParser, ResponseSchema
import transformers

load_dotenv()

transformers.logging.set_verbosity_error()

llm = HuggingFaceEndpoint(
    repo_id = "Qwen/Qwen2.5-7B-Instruct",
    task = "text-generation"
)

model = ChatHuggingFace(llm=llm)

schema = [
    ResponseSchema(name="fact_1", description="The first fact about the topic."),
    ResponseSchema(name="fact_2", description="The second fact about the topic."),  
    ResponseSchema(name="fact_3", description="The third fact about the topic.")
]

parser = StructuredOutputParser.from_response_schemas(schema)

template = PromptTemplate(
    template="Give 3 fact about {topic} \n {format_instruction}",
    input_variables=["topic"],
    partial_variables={"format_instruction": parser.get_format_instructions()}
)

# prompt = template.invoke({"topic":"black hole"})
# result = model.invoke(prompt)
# final_result = parser.parse(result.content)
# print(final_result)


chain = template | model | parser
result = chain.invoke({"topic":"black hole"})
print(result)
