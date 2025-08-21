from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama
from app.kb import db


# ----------------
# STATE DEFINITION
# ----------------
class AgentState(Dict[str, Any]):
    """Shared state that flows between nodes."""
    pass


# ----------------
# LLM SETUP
# ----------------
llm = ChatOllama(model="tinyllama", temperature=0)


# ----------------
# NODE FUNCTIONS
# ----------------

def analyze_ticket(state: AgentState) -> AgentState:
    """Summarize user query + classify intent"""
    query = state["query"]
    summary = llm.invoke(f"Summarize this support ticket: {query}")
    category = llm.invoke(
        f"Classify the intent of this support query into one of: "
        f"[refund, shipping, defect, general]: {query}"
    )
    state["summary"] = str(summary)
    state["category"] = str(category)
    return state


def check_order(state: AgentState) -> AgentState:
    """Call mock API if order_id exists"""
    order_id = state.get("order_id")
    if not order_id:
        state["order_info"] = None
        return state

    import requests
    try:
        resp = requests.get(f"http://127.0.0.1:8001/orders/{order_id}")
        if resp.status_code == 200:
            state["order_info"] = resp.json()
        else:
            state["order_info"] = {"error": "Order not found"}
    except Exception as e:
        state["order_info"] = {"error": str(e)}
    return state


def retrieve_kb(state: AgentState) -> AgentState:
    """Retrieve relevant policies from KB"""
    query = state["query"]
    docs = db.similarity_search(query, k=2)
    state["kb_sources"] = [doc.page_content for doc in docs]
    return state


def draft_reply(state: AgentState) -> AgentState:
    """Combine info into draft reply"""
    context_parts = []
    if state.get("order_info"):
        context_parts.append(f"Order Info: {state['order_info']}")
    if state.get("kb_sources"):
        context_parts.append("KB Info:\n" + "\n".join(state["kb_sources"]))

    prompt = f"""
    User query: {state['query']}
    Ticket summary: {state.get('summary')}
    Category: {state.get('category')}

    Context:
    {context_parts}

    Draft a polite and helpful customer support reply.
    """
    reply = llm.invoke(prompt)
    state["draft"] = str(reply)
    return state


def finalize_response(state: AgentState) -> AgentState:
    """Finalize agent response"""
    state["final_response"] = state.get("draft", "Sorry, I couldn’t process that.")
    return state


# ----------------
# GRAPH CONSTRUCTION
# ----------------
workflow = StateGraph(AgentState)

workflow.add_node("analyze_ticket", analyze_ticket)
workflow.add_node("check_order", check_order)
workflow.add_node("retrieve_kb", retrieve_kb)
workflow.add_node("draft_reply", draft_reply)
workflow.add_node("finalize_response", finalize_response)

workflow.set_entry_point("analyze_ticket")

workflow.add_edge("analyze_ticket", "check_order")
workflow.add_edge("check_order", "retrieve_kb")
workflow.add_edge("retrieve_kb", "draft_reply")
workflow.add_edge("draft_reply", "finalize_response")
workflow.add_edge("finalize_response", END)

memory = MemorySaver()
agent_app = workflow.compile(checkpointer=memory)
