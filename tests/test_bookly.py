import unittest
from datetime import date, timedelta
from bookly.agent import Agent
from bookly.backend import Backend


class BooklyTests(unittest.TestCase):
    def setUp(self):
        self.a = Agent(customer_email='alex@example.com', backend=Backend(today=date(2026,10,27)))

    def prepare(self):
        self.a.dispatch('lookup_order', dict(order_id='BK1002', email='alex@example.com'))
        return self.a.dispatch('prepare_return', dict(order_id='BK1002', item_id='HOBBIT', reason='damaged'))

    def test_account_scope(self):
        orders = self.a.dispatch('list_my_orders', {})['orders']
        self.assertEqual({o['order_id'] for o in orders}, {'BK1001', 'BK1002'})
        self.assertIn('error', self.a.dispatch('lookup_order', dict(order_id='BK1003', email='sam@example.com')))

    def test_tracking_dates(self):
        result = self.a.dispatch('lookup_order', dict(order_id='BK1001', email='alex@example.com'))
        self.assertEqual(result['dispatched_at'], '2026-10-25')
        self.assertEqual(result['eta'], '2026-10-29')
        self.assertTrue(result['tracking_url'].startswith('https://gls-group.com/DK/en/parcel-tracking/?match='))

    def test_distinct_purchased_books(self):
        orders = self.a.backend.orders
        self.assertEqual(set(orders['BK1001']['items']), {'DUNE'})
        self.assertEqual(set(orders['BK1002']['items']), {'HOBBIT', '1984'})

    def test_return_switches_orders_without_reasking_permission(self):
        self.a.dispatch('lookup_order', dict(order_id='BK1001', email='alex@example.com'))
        result = self.a.dispatch('prepare_return', dict(order_id='BK1002', item_id='HOBBIT', reason='damaged on arrival'))
        self.assertTrue(result['requires_confirmation'])
        self.assertEqual(self.a.pending['reason'], 'damaged on arrival')
        self.assertEqual(self.a.verified, 'BK1002')
        self.assertFalse(self.a.backend.returns)

    def test_automatic_return_verification_cannot_access_other_account(self):
        result = self.a.dispatch('prepare_return', dict(order_id='BK1003', item_id='1984', reason='damaged'))
        self.assertIn('error', result)
        self.assertIsNone(self.a.pending)
        self.assertFalse(self.a.backend.returns)

    def test_live_history_and_tracking_link_fallback(self):
        from types import SimpleNamespace
        class Responses:
            def create(inner, **kwargs):
                inner.request = kwargs
                return SimpleNamespace(id='test-response', output=[], usage=None,
                                       output_text='Dune is arriving on October 29.')
        responses = Responses()
        self.a.client = SimpleNamespace(responses=responses)
        self.a.messages = [{'role': 'user', 'content': 'When will Dune arrive?'}]
        self.a.api_input = [{'role': 'user', 'content': 'The Hobbit arrived damaged.'},
                            {'role': 'assistant', 'content': 'I can help with that.'},
                            {'role': 'user', 'content': 'When will Dune arrive?'}]
        self.a.dispatch('lookup_order', dict(order_id='BK1001', email='alex@example.com'))
        answer = self.a.live_reply()
        self.assertIn('[Track with GLS · BK1001](https://gls-group.com/', answer)
        self.assertEqual(responses.request['input'][0]['content'], 'The Hobbit arrived damaged.')

    def test_return_never_shows_unrelated_shipping_links(self):
        self.a.messages = [{'role': 'user', 'content': 'Return 1984, it was damaged on arrival'}]
        self.a.dispatch('list_my_orders', {})
        self.assertEqual(self.a.tracking_links(), {})
        self.a.dispatch('prepare_return', dict(order_id='BK1002', item_id='1984', reason='damaged on arrival'))
        self.assertEqual(self.a.tracking_links(), {})

    def test_tracking_is_scoped_to_requested_order_or_book(self):
        self.a.dispatch('list_my_orders', {})
        for request in ('When will 1984 arrive?', 'Delivery status of BK1002?'):
            self.a.messages = [{'role': 'user', 'content': request}]
            self.assertEqual(self.a.tracking_links(), {})
        self.a.messages = [{'role': 'user', 'content': 'Where is Dune?'}]
        self.assertEqual(set(self.a.tracking_links()), {'BK1001'})

    def test_recommendations(self):
        result = self.a.dispatch('get_recommendations', {})
        self.assertEqual({b['id'] for b in result['recommendations']}, {'LEFT','EARTHSEA'})
        self.assertTrue(all(b['available'] for b in result['recommendations']))

    def test_proposal_confirm_and_duplicate(self):
        self.prepare()
        self.assertFalse(self.a.backend.returns)
        token = self.a.pending['token']
        self.assertIn('RET-0001', self.a.confirm(token))
        self.assertIn('No matching', self.a.confirm(token))
        self.assertEqual(len(self.a.backend.returns), 1)

    def test_policy_boundary_and_revalidation(self):
        backend = self.a.backend
        self.assertIsNotNone(backend.eligibility('BK1003', '1984'))
        self.assertIsNotNone(backend.eligibility('BK1004', 'EBOOK'))
        backend.orders['BK1002']['delivered'] = str(backend.today - timedelta(days=30))
        self.assertIsNone(backend.eligibility('BK1002', 'HOBBIT'))
        self.prepare()
        token = self.a.pending['token']
        backend.orders['BK1002']['delivered'] = str(backend.today - timedelta(days=31))
        self.assertIn('30-day', self.a.confirm(token))
        self.assertFalse(backend.returns)

    def test_tools_and_cancel(self):
        self.assertIn('error', self.a.dispatch('issue_refund', {}))
        self.assertIn('error', self.a.dispatch('lookup_order', {'order_id': 1, 'email':'x'}))
        self.prepare()
        token = self.a.pending['token']
        self.a.cancel()
        self.assertIn('No matching', self.a.confirm(token))
        self.assertFalse(self.a.backend.returns)


if __name__ == '__main__':
    unittest.main()
