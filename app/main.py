# app/main.py
from fastapi import FastAPI
from app.agent import get_agent

app = FastAPI()
agent = get_agent()

@app.get("/")
def root():
    return {"message": "Customer Support Agent is running. Use POST /chat to talk with me."}

@app.post("/chat")
def chat(query: dict):
    q = query.get("query")
    if not q:
        return {"error": "Missing 'query' field"}
    result = agent.run(q)
    return {"response": result}
