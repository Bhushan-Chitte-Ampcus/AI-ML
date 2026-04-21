from langchain_community.document_loaders import CSVLoader

loader = CSVLoader(file_path="./documents/diabetes.csv")

data = loader.load()

# print(data)
print(len(data))
print(data[0])