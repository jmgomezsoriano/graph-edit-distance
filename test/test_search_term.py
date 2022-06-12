import unittest

from grapheditdistance.graph import TextGraph


class MyTestCase(unittest.TestCase):
    def test_search(self):
        g = TextGraph()
        g.index(['hola', 'adiós', 'goodbye', 'punto de venta', 'puerta'])
        results = g.seq_search('pumto de ventas', nbest=0)
        print(results)
        print(g.seq_search('punto', nbest=0))
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
