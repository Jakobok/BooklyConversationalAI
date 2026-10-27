"""Small catalogue and simulated recommendation engine."""
BOOKS = [
    dict(id="DUNE", title="Dune", author="Frank Herbert", genre="Science fiction", price=18, color="#bb603b", ink="#fff0d1"),
    dict(id="HOBBIT", title="The Hobbit", author="J.R.R. Tolkien", genre="Fantasy", price=15, color="#344c3e", ink="#f2dfa5"),
    dict(id="LEFT", title="The Left Hand of Darkness", author="Ursula K. Le Guin", genre="Science fiction", price=16, color="#314d64", ink="#ede3cb"),
    dict(id="EARTHSEA", title="A Wizard of Earthsea", author="Ursula K. Le Guin", genre="Fantasy", price=14, color="#977748", ink="#fff4d4"),
    dict(id="PRIDE", title="Pride and Prejudice", author="Jane Austen", genre="Classics", price=12, color="#816475", ink="#fceadc"),
    dict(id="1984", title="1984", author="George Orwell", genre="Classics", price=12, color="#a34538", ink="#ffe6c3"),
]

DETAILS = {
    'DUNE': ('9780441172719', 'On the desert planet Arrakis, Paul Atreides becomes entangled in a struggle over power, prophecy, and the most precious resource in the universe.'),
    'HOBBIT': ('9780547928227', 'A quiet hobbit leaves his comfortable home for an unexpected adventure with dwarves, a wizard, and a dragon guarding a mountain of gold.'),
    'LEFT': ('9780441478125', 'An envoy travels to an icy world whose people challenge everything he assumes about identity, trust, and belonging.'),
    'EARTHSEA': ('9780547773742', 'A gifted young wizard unleashes a shadow and must journey across an archipelago to understand the balance of magic and the meaning of his own name.'),
    'PRIDE': ('9780141439518', 'Elizabeth Bennet and Mr Darcy navigate family expectations, first impressions, and the surprising possibility of love.'),
    '1984': ('9780451524935', 'In a society shaped by surveillance and rewritten history, Winston Smith begins to question the truths he is told.'),
    'GATSBY': ('9780743273565', 'A glittering summer on Long Island draws Nick Carraway into the mysterious world of Jay Gatsby and an impossible dream.'),
    'FRANKENSTEIN': ('9780141439471', 'A young scientist creates life, then abandons his creation. A haunting story of ambition, loneliness, and responsibility.'),
}
BOOKS.extend([
    dict(id='GATSBY', title='The Great Gatsby', author='F. Scott Fitzgerald', genre='Classics', price=13, color='#214b57', ink='#ffedbd'),
    dict(id='FRANKENSTEIN', title='Frankenstein', author='Mary Shelley', genre='Classics', price=14, color='#55664b', ink='#fff4d4'),
])
for book in BOOKS:
    isbn, description = DETAILS[book['id']]
    book.update(isbn=isbn, description=description,
                cover=f'https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg')


def recommend(backend, email):
    purchased = {item for order in backend.orders.values() if order["email"] == email
                 for item in order["items"]}
    genres = {b["genre"] for b in BOOKS if b["id"] in purchased}
    matches = [{**b, "available": True, "currency": "USD",
                "reason": f"Your purchase history includes {b['genre'].lower()}."}
               for b in BOOKS if b["id"] not in purchased and b["genre"] in genres]
    return {"recommendations": matches[:2], "engine": "Mock genre matching, excludes purchased titles"}
