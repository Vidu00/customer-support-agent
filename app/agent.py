# app/agent.py

from langchain.agents import initialize_agent, Tool
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM

from langchain_community.vectorstores import Chroma



# --- Load the KB (Chroma DB already persisted in Step 5) ---
db = Chroma(persist_directory="chroma_db")  # No need to re-embed, just load


# --- Define LLM (Ollama) ---
llm = OllamaLLM(model="tinyllama")


# --- Define KB Retrieval Tool ---
def search_kb(query: str):
    """Search knowledge base for relevant policy/FAQ info."""
    docs = db.similarity_search(query, k=2)
    return "\n".join([d.page_content for d in docs])


# --- Define Mock API Tool ---
def query_api(order_id: str):
    """Query the mock API for order/product info."""
    try:
        resp = requests.get(f"http://127.0.0.1:8001/order/{order_id}")
        if resp.status_code == 200:
            return resp.json()
        else:
            return f"API Error: {resp.text}"
    except Exception as e:
        return f"Failed to call API: {str(e)}"


# --- Register Tools ---
tools = [
    Tool(
        name="KnowledgeBase",
        func=search_kb,
        description="Useful for answering policy or FAQ-related queries like refund, shipping, defect handling."
    ),
    Tool(
        name="OrderAPI",
        func=query_api,
        description="Use when needing details about an order, delivery status, or product info."
    ),
]


# --- Initialize Agent ---
agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True
)


def get_agent():
    """Return initialized agent"""
    return agent