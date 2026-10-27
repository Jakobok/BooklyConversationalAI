"""Small catalogue and simulated recommendation engine."""
BOOKS = [
    dict(id="DUNE", title="Dune", author="Frank Herbert", genre="Science fiction", price=18, color="#bb603b", ink="#fff0d1"),
    dict(id="HOBBIT", title="The Hobbit", author="J.R.R. Tolkien", genre="Fantasy", price=15, color="#344c3e", ink="#f2dfa5"),
    dict(id="LEFT", title="The Left Hand of Darkness", author="Ursula K. Le Guin", genre="Science fiction", price=16, color="#314d64", ink="#ede3cb"),
    dict(id="EARTHSEA", title="A Wizard of Earthsea", author="Ursula K. Le Guin", genre="Fantasy", price=14, color="#977748", ink="#fff4d4"),
    dict(id="PRIDE", title="Pride and Prejudice", author="Jane Austen", genre="Classics", price=12, color="#816475", ink="#fceadc"),
    dict(id="1984", title="1984", author="George Orwell", genre="Classics", price=12, color="#a34538", ink="#ffe6c3"),
]


def recommend(backend, email):
    purchased = {item for order in backend.orders.values() if order["email"] == email
                 for item in order["items"]}
    genres = {b["genre"] for b in BOOKS if b["id"] in purchased}
    matches = [{**b, "available": True, "currency": "USD",
                "reason": f"Your purchase history includes {b['genre'].lower()}."}
               for b in BOOKS if b["id"] not in purchased and b["genre"] in genres]
    return {"recommendations": matches[:2], "engine": "Mock genre matching, excludes purchased titles"}
