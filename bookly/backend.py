"""Mock commerce boundary. All policies are illustrative Bookly assumptions."""
from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass
class Backend:
    today: date = field(default_factory=date.today)
    orders: dict = field(init=False)
    returns: dict = field(default_factory=dict)

    def __post_init__(self):
        self.orders = {
            "BK1001": {"email": "alex@example.com", "status": "in_transit",
                       "eta": str(self.today + timedelta(days=2)),
                       "tracking": "DEMO-TRACK-101", "delivered": None,
                       "items": {"DUNE": {"title": "Dune", "cents": 1800, "physical": True}}},
            "BK1002": {"email": "alex@example.com", "status": "delivered",
                       "eta": None, "tracking": "DEMO-TRACK-102",
                       "delivered": str(self.today - timedelta(days=7)),
                       "items": {"HOBBIT": {"title": "The Hobbit", "cents": 1500, "physical": True},
                                 "DUNE": {"title": "Dune", "cents": 1800, "physical": True}}},
            "BK1003": {"email": "sam@example.com", "status": "delivered",
                       "eta": None, "tracking": "DEMO-TRACK-103",
                       "delivered": str(self.today - timedelta(days=45)),
                       "items": {"1984": {"title": "1984", "cents": 1200, "physical": True}}},
            "BK1004": {"email": "sam@example.com", "status": "delivered",
                       "eta": None, "tracking": None,
                       "delivered": str(self.today - timedelta(days=2)),
                       "items": {"EBOOK": {"title": "Digital anthology", "cents": 900, "physical": False}}},
        }

    def lookup(self, order_id, email):
        order = self.orders.get(order_id.upper())
        if not order or order["email"].casefold() != email.strip().casefold():
            return {"error": "Order could not be verified. Check order ID and checkout email."}
        return {"order_id": order_id.upper(),
                "dispatched_at": str(self.today - timedelta(days=2)) if order["status"] == "in_transit" else None,
                **{k: v for k, v in order.items() if k != "email"}}

    def eligibility(self, order_id, item_id):
        order = self.orders[order_id]
        item = order["items"].get(item_id)
        if not item:
            return "Choose one item ID from this order."
        if (order_id, item_id) in self.returns:
            return "A return already exists for this item."
        if order["status"] != "delivered":
            return "Returns require a delivered order."
        if not item["physical"]:
            return "Digital purchases require a human review."
        age = (self.today - date.fromisoformat(order["delivered"])).days
        if not 0 <= age <= 30:
            return "Outside the 30-day return window. A human can review an exception."
        return None

    def create_return(self, proposal):
        key = (proposal["order_id"], proposal["item_id"])
        # Idempotent retry at the mock backend boundary.
        if key in self.returns:
            return self.returns[key]
        error = self.eligibility(*key)
        if error:
            return {"error": error}
        result = {"return_id": f"RET-{len(self.returns) + 1:04d}",
                  **proposal, "status": "awaiting_receipt",
                  "instructions": "Demo: pack the book and use the simulated prepaid label. No real label or payment is created."}
        self.returns[key] = result
        return result
