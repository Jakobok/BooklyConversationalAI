import base64
import json
import os
from datetime import timedelta
from html import escape
import streamlit as st
from dotenv import load_dotenv
from bookly.agent import Agent
from bookly.catalog import BOOKS

def avatar_uri(letter, background, ink):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80"><rect width="80" height="80" rx="24" fill="{background}"/><text x="40" y="54" text-anchor="middle" font-family="Georgia,serif" font-size="48" fill="{ink}">{letter}</text></svg>'
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()


AVATARS = {'assistant': avatar_uri('b', '#243b32', '#fff9e9'),
           'user': avatar_uri('J', '#e5e9df', '#243b32')}


load_dotenv()
st.set_page_config(page_title='Bookly | Your next chapter', page_icon='📚', layout='wide')
if 'agent' not in st.session_state or st.session_state.get('bookly_revision') != 'chat-v4':
    st.session_state.agent = Agent('live', customer_email='alex@example.com')
    st.session_state.bookly_revision = 'chat-v4'
for key, value in [('basket', {}), ('chat_open', False), ('receipt', None), ('chat_request', None)]:
    if key not in st.session_state:
        st.session_state[key] = value
agent = st.session_state.agent
has_key = bool(os.getenv('OPENAI_API_KEY'))
books = {b['id']: b for b in BOOKS}
st.markdown('''<style>
.stApp{background:#fbf9f4;color:#243b32}[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1380px;padding:1rem 2rem 6rem}h1,h2,h3{font-family:Georgia,serif!important;color:#243b32!important}
.strip{text-align:center;background:#243b32;color:#fff9e9;padding:9px;font-size:12px;letter-spacing:1px}
.nav{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #dedfd5;padding:24px 0;gap:20px}.logo{font-family:Georgia,serif;font-size:42px;font-weight:bold;letter-spacing:-2px}.navlinks{font-size:13px;color:#68756b}.account{font-size:11px;text-align:right}.account b{display:block;font-size:14px}
.hero{background:#e9eddf;border-radius:8px;padding:42px 48px;margin:24px 0;display:flex;align-items:center;justify-content:space-between;gap:24px}.hero h1{font-size:60px;line-height:1.08;margin:12px 0 20px;font-weight:400}.hero p{max-width:460px;line-height:1.7;color:#5d6c60}.eyebrow{font-size:11px;letter-spacing:2px;text-transform:uppercase}.hero-books{display:flex;gap:18px;padding:10px}.hero-books img{height:230px;width:150px;object-fit:cover;box-shadow:8px 12px 20px #243b3233;transform:rotate(8deg)}.hero-books img:first-child{transform:rotate(-10deg);margin-top:35px}
.benefits{display:flex;justify-content:space-around;border-bottom:1px solid #dedfd5;padding:10px 0 25px;font-size:12px;color:#697566}
.cover{height:265px;background:#f0eee6;border-radius:5px;display:flex;align-items:center;justify-content:center;margin:10px 0 15px}.cover img{height:232px;max-width:85%;object-fit:contain;box-shadow:5px 7px 12px #243b3233;transition:transform .2s}.cover:hover img{transform:translateY(-5px)}.title{font-family:Georgia,serif;font-size:18px;min-height:46px}.author{color:#7b8075;font-size:12px;margin:5px 0}.price{font-weight:600;margin:10px 0}.tag{font-size:10px;color:#5b7359;text-transform:uppercase;letter-spacing:1px}.footer{border-top:1px solid #dedfd5;margin-top:36px;padding:28px 0;color:#7b8075;font-size:12px}
div.stButton>button{border-radius:6px;border-color:#cbd3c4;color:#243b32}div.stButton>button[kind="primary"]{background:#243b32;color:white;border:0}
.st-key-chat_launcher{position:fixed!important;bottom:25px;right:28px;width:175px!important;z-index:999990}.st-key-chat_launcher button{border-radius:30px!important;box-shadow:0 6px 25px #243b3233;padding:14px!important}
.st-key-chat_panel{position:fixed!important;bottom:88px;right:28px;width:600px!important;max-width:calc(100vw - 28px);background:#fffdf8;border:1px solid #d6ddcf;border-radius:18px;padding:18px;box-shadow:0 15px 65px #182e3430;z-index:999989;max-height:calc(100dvh - 115px);overflow:auto}.st-key-chat_panel [data-testid="stChatMessage"]{background:#f0f3eb;border-radius:12px;padding:10px}.st-key-chat_panel h3{font-size:24px!important}.st-key-chat_panel [data-testid="stChatInput"]{position:static!important}.st-key-chat_panel button{font-size:14px}.st-key-chat_panel [data-testid="stVerticalBlock"]{gap:.65rem}.st-key-chat_history{height:clamp(140px,calc(100dvh - 410px),510px)!important}.st-key-chat_panel [data-testid="stChatMessage"] p{font-size:16px;line-height:1.65}.thinking{display:flex;gap:6px;align-items:center;color:#657664;padding:10px}.thinking i{width:7px;height:7px;background:#7b916c;border-radius:50%;animation:pulse 1.3s infinite}.thinking i:nth-child(2){animation-delay:.2s}.thinking i:nth-child(3){animation-delay:.4s}@keyframes pulse{0%,80%,100%{opacity:.3;transform:translateY(0)}40%{opacity:1;transform:translateY(-4px)}}
@media(max-width:750px){.block-container{padding:1rem 1rem 6rem}.hero{padding:28px}.hero h1{font-size:42px}.hero-books,.navlinks{display:none}.benefits{font-size:10px}.st-key-chat_panel{right:14px;bottom:85px}.cover{height:215px}.cover img{height:185px}}
</style>''', unsafe_allow_html=True)


def add_book(bid):
    st.session_state.basket[bid] = st.session_state.basket.get(bid, 0) + 1
    st.toast(f"{books[bid]['title']} added to basket")


def ask(text):
    st.session_state.chat_open = True
    st.session_state.chat_request = text


def toggle_chat():
    st.session_state.chat_open = not st.session_state.chat_open


def send_message():
    ask(st.session_state['chat-message'])


st.markdown('<div class="strip">GOOD STORIES, DELIVERED · Free shipping on orders over $35</div><div class="nav"><div class="logo">bookly<span style="color:#96a677">.</span></div><div class="navlinks">Books &nbsp; / &nbsp; New discoveries &nbsp; / &nbsp; The reading life</div><div class="account">WELCOME BACK<b>John Doe ◉</b></div></div>', unsafe_allow_html=True)
st.markdown(f'''<div class="hero"><div><div class="eyebrow">For the love of a good story</div><h1>A good book changes<br>everything.</h1><p>Extraordinary worlds. Unforgettable characters. Find your next can't-put-it-down read, handpicked for curious minds.</p><div class="eyebrow">Your next chapter starts here ↘</div></div><div class="hero-books"><img src="{BOOKS[1]['cover']}" alt="The Hobbit cover"><img src="{BOOKS[0]['cover']}" alt="Dune cover"></div></div><div class="benefits"><span>✧ Thoughtfully curated books</span><span>↗ Free shipping over $35</span><span>↺ 30-day returns</span></div>''', unsafe_allow_html=True)
browse, orders, basket = st.tabs(['Discover books', 'My orders', f"Basket ({sum(st.session_state.basket.values())})"])
with browse:
    st.subheader('Find a little wonder')
    left, right = st.columns([3, 1])
    search = left.text_input('Search books', placeholder='Search titles or authors…', label_visibility='collapsed')
    sort = right.selectbox('Sort books', ['Curated for you', 'Price: low to high', 'Title: A–Z'], label_visibility='collapsed')
    genre = st.radio('Browse by genre', ['All books'] + sorted({b['genre'] for b in BOOKS}), horizontal=True)
    selected = [b for b in BOOKS if (genre == 'All books' or b['genre'] == genre) and search.casefold() in (b['title'] + b['author']).casefold()]
    if sort == 'Price: low to high':
        selected.sort(key=lambda b: b['price'])
    elif sort == 'Title: A–Z':
        selected.sort(key=lambda b: b['title'])
    st.caption(f'{len(selected)} books · Something worth making time for')
    for offset in range(0, len(selected), 4):
        for col, book in zip(st.columns(4), selected[offset:offset+4]):
            with col:
                st.markdown(f'''<div class="cover"><img src="{book['cover']}" alt="{escape(book['title'], quote=True)} cover" loading="lazy"></div><div class="tag">{book['genre']} · Paperback</div><div class="title">{escape(book['title'])}</div><div class="author">{escape(book['author'])}</div><div class="price">${book['price']:.2f} <span class="author">USD · In stock</span></div>''', unsafe_allow_html=True)
                st.button('Add to basket', key='buy-'+book['id'], type='primary', use_container_width=True, on_click=add_book, args=(book['id'],))
                with st.expander('About this book'):
                    st.write(book['description'])
                    st.button('Ask Bookly about this', key='ask-'+book['id'], disabled=not has_key, on_click=ask, args=(f"Would {book['title']} be a good next read for me?",))
    if not selected:
        st.info('No books found. Try another title or genre.')
with orders:
    st.subheader('Your reading journey')
    for oid, order in agent.backend.orders.items():
        if order['email'] == agent.customer_email:
            with st.container(border=True):
                st.markdown(f"**{oid}** · {order['status'].replace('_', ' ').title()}")
                st.write(', '.join(item['title'] for item in order['items'].values()))
                st.caption(f"Estimated arrival: {order['eta'] or 'Delivered ' + str(order['delivered'])}")
                st.button('Get help with this order', key='order-'+oid, disabled=not has_key, on_click=ask, args=(f'Check status and delivery estimate for {oid}.',))
with basket:
    st.subheader('Your basket')
    if not st.session_state.basket:
        st.info('Your next great read is waiting. Add a book from the shelves.')
    total = 0
    for bid, qty in list(st.session_state.basket.items()):
        total += books[bid]['price'] * qty
        info, remove = st.columns([5, 1])
        info.write(f"**{books[bid]['title']}** · {qty} × ${books[bid]['price']:.2f}")
        if remove.button('Remove', key='remove-'+bid):
            del st.session_state.basket[bid]
            st.rerun()
    if st.session_state.basket:
        shipping = 0 if total >= 35 else 4.95
        st.write(f'Subtotal: **${total:.2f}** · Shipping: **${shipping:.2f}**')
        st.markdown(f'### Total: ${total+shipping:.2f} USD')
        st.caption('Demo checkout · No payment or address needed. Orders last for this session.')
        if st.button('Place demo order', type='primary'):
            oid = f'BK{max(int(k[2:]) for k in agent.backend.orders)+1}'
            agent.backend.orders[oid] = dict(email=agent.customer_email, status='processing', eta=str(agent.backend.today+timedelta(days=5)), tracking=None, delivered=None, items={bid: dict(title=books[bid]['title'], cents=round(books[bid]['price']*100), physical=True, quantity=qty) for bid, qty in st.session_state.basket.items()})
            st.session_state.receipt = f'Thank you, John! Demo order {oid} is confirmed. No payment was taken. Find it in My orders or ask Bookly for its status.'
            st.session_state.basket = {}
            st.rerun()
    if st.session_state.receipt:
        st.success(st.session_state.receipt)
st.markdown('<div class="footer"><b>bookly.</b> &nbsp; A little curiosity goes a long way.<br><br>Fictional bookstore demo · Illustrative prices · No real payments or shipments.<br>Book cover images: Open Library.</div>', unsafe_allow_html=True)
def render_messages():
    if not agent.messages:
        with st.chat_message('assistant', avatar=AVATARS['assistant']):
            st.write('Hi John! Welcome back. What can I help you with today?')
            for label, query in [('Track my order', 'Where is my order?'), ('Return a book', 'I would like to return a book.'), ('Find my next read', 'What would you recommend based on my purchases?')]:
                st.button(label, key='quick-'+label, disabled=not has_key, on_click=ask, args=(query,))
    for index, message in enumerate(agent.messages):
        with st.chat_message(message['role'], avatar=AVATARS[message['role']]):
            st.caption('BOOKLY' if message['role'] == 'assistant' else 'YOU')
            st.write(message['content'])
            if index == len(agent.messages)-1 and message['role'] == 'assistant':
                if agent.pending:
                    p = agent.pending
                    st.caption(f"Expected refund ${p['amount_cents']/100:.2f} after receipt and inspection.")
                    yes, no = st.columns(2)
                    yes.button('Confirm return', key=p['token'], type='primary', on_click=agent.confirm, args=(p['token'],))
                    no.button('Cancel return', on_click=agent.cancel)
                latest = [e for e in agent.events if e.get('turn') == agent.turn and e.get('kind') == 'tool']
                for event_index, event in enumerate(latest):
                    result = event.get('result', {})
                    if event.get('name') == 'list_my_orders' and not agent.pending and 'which' in message['content'].casefold():
                        for order in result.get('orders', []):
                            oid = order['order_id']
                            titles = ', '.join(item['title'] for item in order['items'].values())
                            st.button(f"{titles} · {oid}", key=f'choose-{index}-{event_index}-{oid}', disabled=not has_key, on_click=ask, args=(f'Help me with order {oid}.',))
                    elif event.get('name') == 'get_recommendations':
                        for b in result.get('recommendations', []):
                            st.caption(f"{b['title']} · ${b['price']:.2f}")
                            if st.button('Add '+b['title'], key=f"rec-{index}-{event_index}-{b['id']}"):
                                add_book(b['id'])
                                st.rerun()  # Refresh the basket after this fast local action.
                for oid, url in agent.tracking_links().items():
                    st.link_button(f'Track with GLS · {oid}', url)



@st.fragment
def chat_widget():
    with st.container(key='chat_launcher'):
        st.button('Close chat ✕' if st.session_state.chat_open else '✦ Ask Bookly', type='primary', use_container_width=True, on_click=toggle_chat)
    if not st.session_state.chat_open:
        return
    with st.container(key='chat_panel'):
        heading, close = st.columns([6, 1])
        heading.markdown('### Your Bookly assistant')
        close.button('✕', key='close-chat', on_click=toggle_chat, help='Close conversation')
        st.caption('Your personal bookseller · Orders, returns & recommendations')
        with st.container(height=510, key='chat_history'):
            transcript = st.empty()
            request = st.session_state.pop('chat_request', None)
            if request:
                # Render the customer message and typing indicator BEFORE any API work.
                with transcript.container():
                    for message in agent.messages:
                        with st.chat_message(message['role'], avatar=AVATARS[message['role']]):
                            st.write(message['content'])
                    with st.chat_message('user', avatar=AVATARS['user']):
                        st.write(request)
                    with st.chat_message('assistant', avatar=AVATARS['assistant']):
                        st.markdown('<div class="thinking"><i></i><i></i><i></i><span>&nbsp; Bookly is thinking…</span></div>', unsafe_allow_html=True)
                        with st.spinner('Checking that for you…'):
                            agent.reply(request)
                transcript.empty()
            with transcript.container():
                render_messages()
        if not has_key:
            st.caption('Live chat needs the store API key.')
        st.chat_input('Message Bookly…', disabled=not has_key, max_chars=2000, key='chat-message', on_submit=send_message)
        with st.expander('What Bookly did'):
            st.caption('A simple activity summary for this conversation')
            recent = [e for e in agent.events if e.get('turn') == agent.turn]
            labels = {'list_my_orders': 'Found your orders', 'lookup_order': 'Checked your order details',
                      'get_recommendations': 'Found books matched to your reading history',
                      'prepare_return': 'Checked return eligibility — awaiting your confirmation',
                      'create_return': 'Created your return request — refund follows receipt and inspection'}
            shown = set()
            for event in recent:
                name = event.get('name')
                if name not in labels or name in shown:
                    continue
                shown.add(name)
                result = event.get('result', {})
                if 'error' in result:
                    st.write('• ' + result['error'])
                elif name == 'prepare_return' and not agent.pending:
                    st.write('• Checked return eligibility')
                else:
                    st.write('• ' + labels[name])
            if not shown:
                st.write('No store actions needed yet.')



chat_widget()
