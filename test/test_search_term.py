import unittest

from grapheditdistance.graph import TextGraph


class MyTestCase(unittest.TestCase):
    def test_seq_search_by_default(self):
        g = TextGraph()
        g.index(['hola', 'adiós', 'goodbye', 'punto de venta', 'puerta'])
        # First search
        results = g.seq_search('pumto de ventas', nbest=0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'pumto de ventas')
        self.assertEqual(results[0][1], 'punto de venta')
        self.assertEqual(results[0][2], 2.0)
        path = '[(None), (None), (replace[m -> n], 1), (None), (None), (None), (None), (None), (None), (None), ' \
               '(None), (None), (None), (None), (insert[s], 1), (Final)]'
        self.assertEqual(str(results[0][3]), path)
        # Second search
        results = g.seq_search('punto de venta', nbest=0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'punto de venta')
        self.assertEqual(results[0][1], 'punto de venta')
        self.assertEqual(results[0][2], 0.0)
        path = '[(None), (None), (None), (None), (None), (None), (None), (None), (None), (None), (None), (None), ' \
               '(None), (None), (Final)]'
        self.assertEqual(str(results[0][3]), path)
        # Third search
        results = g.seq_search('puto de vent', nbest=0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'puto de vent')
        self.assertEqual(results[0][1], 'punto de venta')
        self.assertEqual(results[0][2], 2.0)
        path = '[(None), (None), (delete[n], 1), (None), (None), (None), (None), (None), (None), (None), (None), ' \
               '(None), (None), (delete[a], 1), (Final)]'
        self.assertEqual(str(results[0][3]), path)
        results = g.seq_search('punto', nbest=0)
        self.assertListEqual(results, [])  # add assertion here


if __name__ == '__main__':
    unittest.main()
