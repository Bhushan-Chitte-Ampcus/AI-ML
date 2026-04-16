from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda
from dotenv import load_dotenv
import transformers
from pydantic import BaseModel, Field
from typing import Literal

load_dotenv()
transformers.logging.set_verbosity_error()

# -------------------------------------------------------------------------

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="text-generation"
)

model = ChatHuggingFace(
    llm=llm
)

class Feedback(BaseModel):
    sentiment : Literal["positive", "negative"] = Field(description="The sentiment of the feedback")

# -------------------------------------------------------------------------

parser = StrOutputParser()
parser2 = PydanticOutputParser(pydantic_object=Feedback)

# -------------------------------------------------------------------------

prompt1 = PromptTemplate(
    template='Classify the sentiment of the following feedback text into postive or negative \n {feedback} \n {format_instruction}',
    input_variables=['feedback'],
    partial_variables={'format_instruction':parser2.get_format_instructions()}
)

prompt2 = PromptTemplate(
    template='Write an appropriate response to this positive feedback \n {feedback}',
    input_variables=['feedback']
)

prompt3 = PromptTemplate(
    template='Write an appropriate response to this negative feedback \n {feedback}',
    input_variables=['feedback']
)

# -------------------------------------------------------------------------

classifier_chain = prompt1 | model | parser2

branch_chain = RunnableBranch(
    (lambda x:x.sentiment=="positive", prompt2 | model | parser),
    (lambda x:x.sentiment=="negative", prompt3 | model | parser),
    RunnableLambda(lambda x: "could not find sentiment")
)

chain = classifier_chain | branch_chain

# -------------------------------------------------------------------------

result = chain.invoke({"feedback": "This is a beautiful phone"})
print(result)

# -------------------------------------------------------------------------

chain.get_graph().print_ascii()

# -------------------------------------------------------------------------
