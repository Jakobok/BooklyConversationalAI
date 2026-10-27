# Bookly storefront demo

A fictional bookstore with a browsable catalogue, a simulated John Doe login, and
an embedded live OpenAI assistant. Python + Streamlit + direct Responses API tools.
Business data and actions are mocked. The chat UI has no scripted mode.

## Run

Use Python 3.10+ from this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env to set OPENAI_API_KEY
.\.venv\Scripts\python -m streamlit run app.py
```

On macOS/Linux use `.venv/bin/python` and `cp .env.example .env`.
Open http://localhost:8501. Without a server API key the catalogue works, but chat
is disabled. Never place the key in source code or commit .env.

## Hosting

The code is hosted at https://github.com/Jakobok/BooklyConversationalAI. In Streamlit Community
Cloud connect the repository, choose streamlit_app.py, and add root-level secrets:

```toml
OPENAI_API_KEY = "your-key"
OPENAI_MODEL = "gpt-4.1-mini"
```

Root-level Streamlit secrets become environment variables. Pick a Responses model
available in your account. No hosting deployment has been performed in this chat.
The local environment blocked package downloads, so browser rendering and a live
API call still require verification on your machine or hosting service.

## Demo

John is already signed in using a fictional server session. No real authentication.
Ask “Where is my order?” and clarify which order when asked. BK1001 is in transit,
with a dispatch date and arrival estimate. BK1002 contains two delivered books.
Ask to return one, clarify the book and reason, then click Confirm return.
The app creates a simulated return record, not a payment or real shipping label.
Ask “What would you recommend based on my purchases?” to call a small simulated
recommendation engine. It matches genres and excludes purchased titles.

The catalogue is illustrative, with original typographic cover treatments and
fictional prices. Search/category filters and order tabs work. Checkout is outside scope.

## Architecture

app.py renders the store and embedded chat. bookly/agent.py explicitly sends tool
schemas, dispatches function calls, preserves output items and returns tool results
via call_id. bookly/backend.py enforces return eligibility, and bookly/catalog.py
supplies the catalogue and recommendation engine. Session history lives in memory.
The model may look up orders and propose returns, but only a UI confirmation can
commit an action. Policy is rechecked at execution. Duplicate returns are prevented
within one session. A new message invalidates any old confirmation token.

Assumed return policy: physical books within 30 days of delivery, one item per
return, free return shipping, original shipping excluded, refund after receipt and
inspection within 5–10 business days. Exceptions need human review, which is only
suggested, not integrated. All currency is USD.

The inspector shows tool events and receipts, not private model reasoning. It hides
lookup email arguments, but free-text reasons may contain personal information.
Use fictional data only. Production would need authenticated identity, durable
state and idempotency, real integrations, escalation, and conversation evaluations.

## Tests

```powershell
python -m unittest discover -s tests -v
```

Six offline tests exercise actual business/tool boundaries. Live model behavior
and the rendered Streamlit layout require a separate smoke test.

Official API reference used:
https://developers.openai.com/api/docs/guides/function-calling
