import unittest

from grapheditdistance.distances import WeightedLevenshtein
from grapheditdistance.graph import TextGraph

TERMS = ['hello', 'bye', 'goodbye', 'point of sale', 'pointing']


class MyTestCase(unittest.TestCase):
    def test_case_insensitive(self) -> None:
        g = TextGraph()
        g.index(TERMS)
        # First search
        results = g.seq_search('Poimt of sales', nbest=0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'poimt of sales')
        self.assertEqual(results[0][1], 'point of sale')
        self.assertEqual(results[0][2], 2.0)
        path = '[(None), (None), (None), (replace[m -> n], 1), (None), (None), (None), (None), (None), (None), ' \
               '(None), (None), (None), (insert[s], 1), (Final)]'
        self.assertEqual(str(results[0][3]), path)
        # Second search
        results = g.seq_search('point of sale', nbest=0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'point of sale')
        self.assertEqual(results[0][1], 'point of sale')
        self.assertEqual(results[0][2], 0.0)
        path = '[(None), (None), (None), (None), (None), (None), (None), (None), (None), (None), (None), (None), ' \
               '(None), (Final)]'
        self.assertEqual(str(results[0][3]), path)
        # Third search
        results = g.seq_search('poit of sal', nbest=0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'poit of sal')
        self.assertEqual(results[0][1], 'point of sale')
        self.assertEqual(results[0][2], 2.0)
        path = '[(None), (None), (None), (delete[n], 1), (None), (None), (None), (None), (None), (None), (None), ' \
               '(None), (delete[e], 1), (Final)]'
        self.assertEqual(str(results[0][3]), path)
        results = g.seq_search('punto', nbest=0)
        self.assertListEqual(results, [])  # add assertion here

    def test_case_sensitive(self) -> None:
        g = TextGraph(False)
        g.index(TERMS)
        # First search
        results = g.seq_search('Poimt of sales', nbest=0)
        self.assertEqual(len(results), 0)
        # Second search
        results = g.seq_search('Poimt of sale', nbest=0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'Poimt of sale')
        self.assertEqual(results[0][1], 'point of sale')
        self.assertEqual(results[0][2], 2.0)
        path = '[(replace[P -> p], 1), (None), (None), (replace[m -> n], 1), (None), (None), (None), (None), (None), ' \
               '(None), (None), (None), (None), (Final)]'
        self.assertEqual(str(results[0][3]), path)

    def test_weighted_levenshtein(self) -> None:
        lev = WeightedLevenshtein()
        lev.add_insert_cost(' ', 0.1)
        lev.add_delete_cost(' ', 0.1)
        lev.add_replace_cost(' ', '-', 0.1)
        lev.add_replace_cost('-', ' ', 0.1)
        tree = TextGraph(distance=lev)
        tree.index(TERMS)
        results = tree.seq_search('Poi ntof-sales', nbest=0)
        self.assertEqual(len(results), 4)
        path = '[(None), (None), (None), (insert[ ], 0.1), (None), (None), (delete[ ], 0.1), (None), (None), ' \
               '(replace[- ->  ], 0.1), (None), (None), (None), (None), (insert[s], 1), (Final)]'
        self.assertEqual(results[0][0], 'poi ntof-sales')
        self.assertEqual(results[0][1], 'point of sale')
        self.assertEqual(results[0][2], 1.3)
        self.assertEqual(str(results[0][3]), path)
        path = '[(None), (None), (None), (insert[ ], 0.1), (None), (None), (delete[ ], 0.1), (None), (None), ' \
               '(delete[ ], 0.1), (insert[-], 1), (None), (None), (None), (None), (insert[s], 1), (Final)]'
        self.assertEqual(results[1][0], 'poi ntof-sales')
        self.assertEqual(results[1][1], 'point of sale')
        self.assertEqual(results[1][2], 2.3)
        self.assertEqual(str(results[1][3]), path)
        path = '[(None), (None), (None), (insert[ ], 0.1), (None), (None), (delete[ ], 0.1), (None), (None), ' \
               '(replace[- ->  ], 0.1), (None), (None), (None), (insert[e], 1), (replace[s -> e], 1), (Final)]'
        self.assertEqual(results[2][0], 'poi ntof-sales')
        self.assertEqual(results[2][1], 'point of sale')
        self.assertEqual(results[2][2], 2.3)
        self.assertEqual(str(results[2][3]), path)
        path = '[(None), (None), (None), (insert[ ], 0.1), (None), (None), (delete[ ], 0.1), (None), (None), ' \
               '(insert[-], 1), (delete[ ], 0.1), (None), (None), (None), (None), (insert[s], 1), (Final)]'
        self.assertEqual(results[3][0], 'poi ntof-sales')
        self.assertEqual(results[3][1], 'point of sale')
        self.assertEqual(results[3][2], 2.3)
        self.assertEqual(str(results[3][3]), path)


if __name__ == '__main__':
    unittest.main()
