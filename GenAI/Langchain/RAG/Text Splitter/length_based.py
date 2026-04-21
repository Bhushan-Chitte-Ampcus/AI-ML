from langchain_text_splitters import CharacterTextSplitter

text = """
An "agent" is any entity (artificial or not) that perceives and takes actions in the world. A rational agent has goals or preferences and takes actions to make them happen.[d][30] In automated planning, the agent has a specific goal.[31] In automated decision-making, the agent has preferences—there are some situations it would prefer to be in, and some situations it is trying to avoid. The decision-making agent assigns a number to each situation (called the "utility") that measures how much the agent prefers it. For each possible action, it can calculate the "expected utility": the utility of all possible outcomes of the action, weighted by the probability that the outcome will occur. It can then choose the action with the maximum expected utility.
"""

splitter = CharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=0,
    separator=""
)

result = splitter.split_text(text)
print(result[0])

# ------------------------------------------------------------------------------------------------------------------

# from langchain.text_splitter import CharacterTextSplitter
# from langchain_community.document_loaders import PyPDFLoader

# loader = PyPDFLoader("./documents/dl-curriculum.pdf")
# docs = loader.load()

# splitter = CharacterTextSplitter(
#     chunk_size=200,
#     chunk_overlap=0,
#     separator=""
# )

# result = splitter.split_documents(docs)
# print(result)
# print(result[0])
# print(result[0].page_content)