import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# 1. Path to KB
KB_PATH = "kb"

# 2. Load markdown docs
loader = DirectoryLoader(KB_PATH, glob="*.md")
docs = loader.load()

# 3. Use Ollama embeddings (TinyLlama etc.)
embeddings = OllamaEmbeddings(model="tinyllama")

# 4. Create Chroma DB
db = Chroma.from_documents(docs, embeddings, persist_directory="chroma_db")

print("✅ KB indexed and stored in Chroma.")
