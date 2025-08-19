import csv
import json
import random
import datetime
import uuid
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
TICKETS_FILE = BASE_DIR / "tickets.csv"
CUSTOMERS_FILE = BASE_DIR / "customers.json"
ORDERS_FILE = BASE_DIR / "orders.json"

# --- Config ---
NUM_TICKETS = 80
NUM_CUSTOMERS = 40
NUM_ORDERS = 60

CATEGORIES = ["refund", "delivery", "defect", "other"]
PRODUCTS = ["Aurora Headphones", "Nimbus Keyboard", "Bolt Charger", "Terra Bottle", "Luma Lamp"]
CHANNELS = ["email", "chat", "webform"]
STATUSES = ["processing", "shipped", "delivered", "returned", "cancelled"]

# --- Generate customers ---
customers = []
for i in range(NUM_CUSTOMERS):
    cid = f"C{1000+i}"
    customers.append({
        "customer_id": cid,
        "name": f"Customer {i}",
        "email": f"customer{i}@example.com",
        "loyalty": random.choice(["bronze","silver","gold"])
    })

CUSTOMERS_FILE.write_text(json.dumps(customers, indent=2))

# --- Generate orders ---
orders = []
for i in range(NUM_ORDERS):
    oid = f"O{2000+i}"
    orders.append({
        "order_id": oid,
        "customer_id": random.choice(customers)["customer_id"],
        "product": random.choice(PRODUCTS),
        "status": random.choice(STATUSES),
        "last_update": (datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(0,30))).isoformat(),
        "total_amount": round(random.uniform(10, 250), 2)
    })

ORDERS_FILE.write_text(json.dumps(orders, indent=2))

# --- Ticket templates ---
TICKET_TEMPLATES = [
    ("refund", "I received the wrong color for my {product} and want a refund. Order ID: {order_id}"),
    ("delivery", "My package {order_id} hasn’t arrived yet. Tracking hasn’t updated in days."),
    ("defect", "The {product} I bought (order {order_id}) is not working properly."),
    ("other", "I need to update my account information. Can you help?")
]

# --- Generate tickets ---
tickets = []
for i in range(NUM_TICKETS):
    cat, tmpl = random.choice(TICKET_TEMPLATES)
    maybe_order = random.choice([True, False])
    order = random.choice(orders) if maybe_order else None
    text = tmpl.format(product=order["product"] if order else "item",
                       order_id=order["order_id"] if order else "")
    tickets.append({
        "ticket_id": str(uuid.uuid4())[:8],
        "customer_id": random.choice(customers)["customer_id"],
        "channel": random.choice(CHANNELS),
        "text": text.strip(),
        "created_at": datetime.datetime.utcnow().isoformat(),
        "order_id": order["order_id"] if order else ""
    })

# Write tickets CSV
with open(TICKETS_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(tickets[0].keys()))
    writer.writeheader()
    writer.writerows(tickets)

print(f"Synthetic data generated:\n- Tickets: {TICKETS_FILE}\n- Customers: {CUSTOMERS_FILE}\n- Orders: {ORDERS_FILE}")
