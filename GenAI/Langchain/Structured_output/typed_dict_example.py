from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Optional, Literal
import transformers

load_dotenv()

transformers.logging.set_verbosity_error()

llm = HuggingFaceEndpoint(
    repo_id = "Qwen/Qwen2.5-7B-Instruct",
    task = "text-generation"
)

model = ChatHuggingFace(llm=llm)

# Schema
class Review(TypedDict):
    # ------------------------------------------------------------------------------------------------------

    # summary : str
    # sentiment : str

    # ------------------------------------------------------------------------------------------------------

    # summary : Annotated[str, "A brief summary of the review"]
    # sentiment : Annotated[str, "Retuen statement of the review either negative, positive or neutral"]

    # ------------------------------------------------------------------------------------------------------

    key_themes = Annotated[list[str], "write down all the key themes discussed in the review in a list"]
    summary : Annotated[str, "A brief summary of the review"]
    sentiment : Annotated[Literal["pos", "neg"], "Retuen statement of the review either negative, positive or neutral"]
    pros : Annotated[Optional[list[str]], "write down all the pros inside a list"]
    cons : Annotated[Optional[list[str]], "write down all the cons inside a list"]

    # ------------------------------------------------------------------------------------------------------

structured_model = model.with_structured_output(Review)

# user_input = """
# The hardware is great, but the software feels bloated. There are too many pre-installed apps that I can't remove. Also, the UI looks outdated compared to other brands. Hoping for a software to fix this.
# """

user_input = """
I recently upgraded to the Samsung Galaxy S24 Ultra, and I must say, it's an absolute powerhouse! The Snapdragon 8 Gen 3 processor makes everything lightning fast—whether I'm gaming, multitasking, or editing photos. The 5000mAh battery easily lasts a full day even with heavy use, and the 45W fast charging is a lifesaver.

The S-Pen integration is a great touch for note-taking and quick sketches, though I don't use it often. What really blew me away is the 200MP camera—the night mode is stunning, capturing crisp, vibrant images even in low light. Zooming up to 100x actually works well for distant objects, but anything beyond 30x loses quality.

However, the weight and size make it a bit uncomfortable for one-handed use. Also, Samsung's One UI still comes with bloatware—why do I need five different Samsung apps for things Google already provides? The $1,300 price tag is also a hard pill to swallow.

Pros:
Insanely powerful processor (great for gaming and productivity)
Stunning 200MP camera with incredible zoom capabilities
Long battery life with fast charging
S-Pen support is unique and useful

Cons:
Bulky and heavy—not great for one-handed use
Bloatware still exists in One UI
Expensive compared to competitors
"""

result = structured_model.invoke(user_input)

print(result)
