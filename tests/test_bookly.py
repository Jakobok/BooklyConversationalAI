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
