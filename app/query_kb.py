from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# Load DB
db = Chroma(persist_directory="chroma_db", embedding_function=OllamaEmbeddings(model="tinyllama"))

query = "What is your refund policy?"
results = db.similarity_search(query, k=2)

for res in results:
    print(f"Source: {res.metadata}")
    print(res.page_content)
    print("---")
