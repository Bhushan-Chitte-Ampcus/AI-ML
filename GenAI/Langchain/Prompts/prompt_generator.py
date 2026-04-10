from langchain_core.prompts import PromptTemplate
from langchain_core.load import dumpd
import json

# Create Prompt Template
template = PromptTemplate(
    template="""
Please summarize the research paper titled "{paper_input}" with the following specifications:

Explanation Style: {style_input}
Explanation Length: {length_input}

1. Mathematical Details:
- Include relevant mathematical equations if present in the paper.
- Explain the mathematical concepts using simple, intuitive code snippets where applicable.

2. Analogies:
- Use relatable analogies to simplify complex ideas.

If certain information is not available in the paper, respond with:
"Insufficient information available" instead of guessing.

Ensure the summary is clear, accurate, and aligned with the provided style and length.
""",
    input_variables=["paper_input", "style_input", "length_input"],
    validate_template=True
)

# Convert prompt to dictionary
prompt_dict = dumpd(template)

# Save as JSON
with open("./Prompts/template.json", "w") as f:
    json.dump(prompt_dict, f, indent=4)

print("Prompt saved successfully in JSON format.")