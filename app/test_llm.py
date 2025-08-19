from langchain_ollama import OllamaLLM

# Connect to TinyLlama running in Ollama
llm = OllamaLLM(model="tinyllama")

# Test it
response = llm.invoke("Explain what customer support means in one sentence.")
print(response)
