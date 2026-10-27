import json
import os
from html import escape
import streamlit as st
from dotenv import load_dotenv
from bookly.agent import Agent
from bookly.catalog import BOOKS

load_dotenv()
st.set_page_config(page_title='Bookly — Find your next chapter', page_icon='📖', layout='wide')
st.markdown('''<style>
.stApp{background:#faf8f2;color:#263b32} [data-testid="stHeader"]{background:transparent}
.block-container{max-width:1450px;padding-top:1.5rem}
h1,h2,h3{font-family:Georgia,serif!important;color:#263b32!important}
.nav{display:flex;justify-content:space-between;align-items:center;padding:12px 0 25px;border-bottom:1px solid #dcded3;margin-bottom:28px;gap:18px;flex-wrap:wrap}
.logo{font-family:Georgia,serif;font-size:38px;font-weight:bold;letter-spacing:-2px}
.navlinks{color:#647167;font-size:14px}.account{font-size:12px;text-align:right}.account strong{display:block;font-size:15px}
.hero{padding:26px 0 28px}.eyebrow{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#798476;margin-bottom:18px}
.hero h1{font-size:60px;line-height:1.08;font-weight:400;margin:0 0 20px}.hero p{font-size:16px;color:#6e776d;max-width:510px;line-height:1.7}
.book{height:225px;padding:22px 18px 16px;margin:8px 0 15px;box-shadow:5px 7px 12px #263b321c;border-left:7px solid #0002;display:flex;flex-direction:column;justify-content:space-between;border-radius:1px 5px 5px 1px}
.book .label{font-size:9px;letter-spacing:2px}.book .title{font-family:Georgia,serif;font-size:28px;line-height:1.1}.book .author{font-size:10px;letter-spacing:1px;text-transform:uppercase}
.book-meta{font-size:12px;color:#7b8075;min-height:42px}.book-name{font-family:Georgia,serif;font-size:18px;margin:0 0 5px}
.chat-title{font-family:Georgia,serif;font-size:25px}.chat-sub{font-size:12px;color:#72806f;margin:6px 0 20px}
.footer{border-top:1px solid #dcded3;margin-top:36px;padding-top:18px;color:#8b9185;font-size:11px;line-height:1.6}
div.stButton>button{border-radius:5px;border-color:#ccd4c4;background:#faf8f2;color:#34513b}
[data-testid="stChatMessage"]{background:#f1f3eb;border-radius:10px;padding:12px}
@media(max-width:700px){.hero h1{font-size:42px}.navlinks{display:none}}
</style>''', unsafe_allow_html=True)
st.markdown('''<div class="nav"><div class="logo">bookly<span style="color:#9da879">.</span></div><div class="navlinks">Independent books. Endless possibilities.</div><div class="account">YOUR READING CORNER<strong>John Doe &nbsp; ◉</strong></div></div>''', unsafe_allow_html=True)
if 'agent' not in st.session_state:
    st.session_state.agent = Agent('live', customer_email='alex@example.com')
agent = st.session_state.agent
has_key = bool(os.getenv('OPENAI_API_KEY'))


def ask(text):
    with st.spinner('Bookly is checking…'):
        agent.reply(text)
    st.rerun()


store, assistant = st.columns([1.8, 1], gap='large')
with store:
    st.markdown('''<div class="hero"><div class="eyebrow">A little curiosity goes a long way</div><h1>Your next chapter<br>starts here.</h1><p>Welcome back, John. Rediscover an old favourite, explore a different world, or find the book you didn’t know you needed.</p></div>''', unsafe_allow_html=True)
    browse, orders = st.tabs(['Browse the shelves', 'Your orders'])
    with browse:
        search = st.text_input('Find a book', placeholder='Search by title or author…', label_visibility='collapsed')
        genre = st.radio('Bookshelves', ['All books', 'Science fiction', 'Fantasy', 'Classics'], horizontal=True, label_visibility='collapsed')
        selected = [b for b in BOOKS if (genre == 'All books' or b['genre'] == genre) and search.casefold() in (b['title'] + b['author']).casefold()]
        if not selected:
            st.info('No books on this shelf match your search.')
        for offset in range(0, len(selected), 3):
            for col, book in zip(st.columns(3), selected[offset:offset+3]):
                with col:
                    st.markdown(f'''<div class="book" style="background:{book['color']};color:{book['ink']}"><div class="label">BOOKLY EDITIONS</div><div class="title">{escape(book['title'])}</div><div class="author">{escape(book['author'])}</div></div><div class="book-name">{escape(book['title'])}</div><div class="book-meta">{escape(book['author'])}<br>${book['price']:.2f} USD</div>''', unsafe_allow_html=True)
                    if st.button('Ask about this book', key=book['id'], disabled=not has_key, use_container_width=True):
                        ask(f"Based on my purchase history, would {book['title']} be a good next read? Check your recommendations.")
    with orders:
        st.caption('John’s sample orders. Dates are relative to today.')
        for oid, order in agent.backend.orders.items():
            if order['email'] != agent.customer_email:
                continue
            with st.container(border=True):
                st.markdown(f"**{oid}** · {order['status'].replace('_', ' ').title()}")
                st.write(', '.join(item['title'] for item in order['items'].values()))
                st.caption(f"Expected arrival: {order['eta'] or 'Delivered ' + str(order['delivered'])}")
                if st.button('Ask about order', key='order-' + oid, disabled=not has_key):
                    ask(f'What is the status of {oid}? When was it sent and when should it arrive?')
    st.markdown('<div class="footer">BOOKLY · A fictional independent bookstore<br>Demo account: John Doe. Catalogue, orders and business actions are simulated. No checkout or real payments.</div>', unsafe_allow_html=True)
with assistant:
    with st.container(border=True):
        st.markdown('<div class="chat-title">Your Bookly assistant</div><div class="chat-sub">Here for your orders. And your next great read.</div>', unsafe_allow_html=True)
        with st.container(height=460):
            if not agent.messages:
                with st.chat_message('assistant'):
                    st.write('Hi John! How can I help today? I can check your orders, help with a return, or find your next read.')
            for message in agent.messages:
                with st.chat_message(message['role']):
                    st.write(message['content'])
        if agent.pending:
            p = agent.pending
            st.info(f"Return {p['item_id']} from {p['order_id']} · {p['reason']} · expected refund ${p['amount_cents']/100:.2f} after receipt and inspection.")
            yes, no = st.columns(2)
            if yes.button('Confirm return', key=p['token'], type='primary'):
                agent.confirm(p['token'])
                st.rerun()
            if no.button('Cancel'):
                agent.cancel()
                st.rerun()
        if not has_key:
            st.warning('Live chat needs an OpenAI API key in the server settings. The storefront is ready to browse.')
        if text := st.chat_input('Ask Bookly anything…', disabled=not has_key, max_chars=2000):
            ask(text)
        for col, label, query in zip(st.columns(3), ['Track order', 'Start return', 'Find a book'], ['Where is my order?', 'I would like to return a book.', 'What would you recommend based on my past purchases?']):
            if col.button(label, disabled=not has_key, use_container_width=True):
                ask(query)
    with st.expander('Behind the conversation'):
        st.caption('Live OpenAI conversation · simulated commerce tools · demo login')
        for event in reversed(agent.events):
            st.json(event, expanded=False)
        st.download_button('Download trace', json.dumps(agent.events, indent=2), 'bookly-trace.json')
        if st.button('Reset demo'):
            del st.session_state.agent
            st.rerun()
