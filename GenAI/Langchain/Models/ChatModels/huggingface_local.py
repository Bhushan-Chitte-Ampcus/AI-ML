from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
import os
import transformers
from dotenv import load_dotenv

load_dotenv()

transformers.logging.set_verbosity_error()


os.environ["HF_HOME"] = "D:/huggingface_cache"
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

llm = HuggingFacePipeline.from_model_id(
    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    # model_id="Qwen/Qwen2.5-7B-Instruct",
    task = "text-generation",
    pipeline_kwargs= dict(
        temperature = 0.5,
        max_new_tokens = 100
    )
)

model = ChatHuggingFace(llm=llm)

result = model.invoke("what is the capital of india?")
# result = model.invoke("what is Generative AI")
print(result.content)
