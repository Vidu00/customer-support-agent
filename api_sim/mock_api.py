# api_sim/mock_api.py
from __future__ import annotations
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
from typing import List, Optional
import json

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
ORDERS_PATH = DATA_DIR / "orders.json"
CUSTOMERS_PATH = DATA_DIR / "customers.json"

# ---------- Data models ----------
class Customer(BaseModel):
    customer_id: str
    name: str
    email: str
    loyalty: Optional[str] = Field(default=None, description="bronze/silver/gold")

class Order(BaseModel):
    order_id: str
    customer_id: str
    product: str
    status: str  # processing | shipped | delivered | returned | cancelled
    last_update: str
    total_amount: float

# ---------- In-memory stores (filled at startup / reload) ----------
CUSTOMERS: dict[str, Customer] = {}
ORDERS: dict[str, Order] = {}

def _safe_read_json(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))

def load_data() -> None:
    global CUSTOMERS, ORDERS
    customers_raw = _safe_read_json(CUSTOMERS_PATH)
    orders_raw = _safe_read_json(ORDERS_PATH)
    CUSTOMERS = {c["customer_id"]: Customer(**c) for c in customers_raw}
    ORDERS = {o["order_id"]: Order(**o) for o in orders_raw}

# ---------- App ----------
app = FastAPI(
    title="RetailCo Mock External API",
    description="Simulated external system for orders/customers. Used by the agent to fetch context.",
    version="1.0.0",
)

# CORS so your Streamlit/Gradio UI can call this API from a different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local demo only
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data at startup
@app.on_event("startup")
def _startup():
    load_data()

# ---------- Health ----------
@app.get("/health")
def health():
    return {"ok": True, "orders": len(ORDERS), "customers": len(CUSTOMERS)}

# ---------- Customers ----------
@app.get("/customers", response_model=List[Customer])
def list_customers(q: str | None = Query(default=None, description="Search by name or email (contains)")):
    vals = list(CUSTOMERS.values())
    if q:
        qlow = q.lower()
        vals = [c for c in vals if qlow in c.name.lower() or qlow in c.email.lower()]
    return vals

@app.get("/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: str):
    c = CUSTOMERS.get(customer_id)
    if not c:
        raise HTTPException(404, "Customer not found")
    return c

# ---------- Orders ----------
@app.get("/orders", response_model=List[Order])
def list_orders(
    customer_id: str | None = Query(default=None),
    status: str | None = Query(default=None, description="processing|shipped|delivered|returned|cancelled"),
    q: str | None = Query(default=None, description="Search by product (contains)")
):
    vals = list(ORDERS.values())
    if customer_id:
        vals = [o for o in vals if o.customer_id == customer_id]
    if status:
        vals = [o for o in vals if o.status.lower() == status.lower()]
    if q:
        qlow = q.lower()
        vals = [o for o in vals if qlow in o.product.lower()]
    return vals

@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    o = ORDERS.get(order_id)
    if not o:
        raise HTTPException(404, "Order not found")
    return o

# ---------- Utility ----------
@app.post("/__reload")
def reload_data():
    """
    Reload data from JSON files without restarting the server.
    Useful after regenerating synthetic data.
    """
    load_data()
    return {"reloaded": True, "orders": len(ORDERS), "customers": len(CUSTOMERS)}
