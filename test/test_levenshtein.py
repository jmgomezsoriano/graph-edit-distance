import unittest

from grapheditdistance.distances import WeightedLevenshtein
from grapheditdistance import TextGraph, Graph

TERMS = ['hello', 'bye', 'goodbye', 'point of sale', 'pointing']


class MyTestCase(unittest.TestCase):
    def test_case_insensitive(self) -> None:
        g = TextGraph()
        g.index([t.lower() for t in TERMS])
        # First search
        results = g.search('Poimt of sales'.lower(), nbest=0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'point of sale')
        self.assertEqual(results[0][1], 2.0)
        path = '[(None), (None), (None), (replace[m -> n], 1), (None), (None), (None), (None), (None), (None), ' \
               '(None), (None), (None), (insert[s], 1), (Final)]'
        self.assertEqual(str(results[0][2]), path)
        # Second search
        results = g.search('point of sale'.lower(), nbest=0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'point of sale')
        self.assertEqual(results[0][1], 0.0)
        path = '[(None), (None), (None), (None), (None), (None), (None), (None), (None), (None), (None), (None), ' \
               '(None), (Final)]'
        self.assertEqual(str(results[0][2]), path)
        # Third search
        results = g.search('poit of sal'.lower(), nbest=0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'point of sale')
        self.assertEqual(results[0][1], 2.0)
        path = '[(None), (None), (None), (delete[n], 1), (None), (None), (None), (None), (None), (None), (None), ' \
               '(None), (delete[e], 1), (Final)]'
        self.assertEqual(str(results[0][2]), path)
        results = g.search('punto', nbest=0)
        self.assertListEqual(results, [])  # add assertion here

    def test_case_sensitive(self) -> None:
        g = TextGraph()
        g.index(TERMS)
        # First search
        results = g.search('Poimt of sales', nbest=0)
        self.assertEqual(len(results), 0)
        # Second search
        results = g.search('Poimt of sale', nbest=0)
        self.assertEqual(len(results), 1)
        # self.assertEqual(results[0][0], 'Poimt of sale')
        self.assertEqual(results[0][0], 'point of sale')
        self.assertEqual(results[0][1], 2.0)
        path = '[(replace[P -> p], 1), (None), (None), (replace[m -> n], 1), (None), (None), (None), (None), (None), ' \
               '(None), (None), (None), (None), (Final)]'
        self.assertEqual(str(results[0][2]), path)

    def test_weighted_levenshtein(self) -> None:
        lev = WeightedLevenshtein()
        lev.add_insert_cost(' ', 0.1)
        lev.add_delete_cost(' ', 0.1)
        lev.add_replace_cost(' ', '-', 0.1)
        lev.add_replace_cost('-', ' ', 0.1)
        tree = TextGraph(distance=lev)
        tree.index([t.lower() for t in TERMS])
        results = tree.search('Poi ntof-sales'.lower(), nbest=0)
        self.assertEqual(len(results), 4)
        path = '[(None), (None), (None), (insert[ ], 0.1), (None), (None), (delete[ ], 0.1), (None), (None), ' \
               '(replace[- ->  ], 0.1), (None), (None), (None), (None), (insert[s], 1), (Final)]'
        self.assertEqual(results[0][0], 'point of sale')
        self.assertEqual(results[0][1], 1.3)
        self.assertEqual(str(results[0][2]), path)
        path = '[(None), (None), (None), (insert[ ], 0.1), (None), (None), (delete[ ], 0.1), (None), (None), ' \
               '(delete[ ], 0.1), (insert[-], 1), (None), (None), (None), (None), (insert[s], 1), (Final)]'
        self.assertEqual(results[1][0], 'point of sale')
        self.assertEqual(results[1][1], 2.3)
        self.assertEqual(str(results[1][2]), path)
        path = '[(None), (None), (None), (insert[ ], 0.1), (None), (None), (delete[ ], 0.1), (None), (None), ' \
               '(replace[- ->  ], 0.1), (None), (None), (None), (insert[e], 1), (replace[s -> e], 1), (Final)]'
        self.assertEqual(results[2][0], 'point of sale')
        self.assertEqual(results[2][1], 2.3)
        self.assertEqual(str(results[2][2]), path)
        path = '[(None), (None), (None), (insert[ ], 0.1), (None), (None), (delete[ ], 0.1), (None), (None), ' \
               '(insert[-], 1), (delete[ ], 0.1), (None), (None), (None), (None), (insert[s], 1), (Final)]'
        self.assertEqual(results[3][0], 'point of sale')
        self.assertEqual(results[3][1], 2.3)
        self.assertEqual(str(results[3][2]), path)

    def test_preprocess(self) -> None:
        from grapheditdistance import TextGraph

        # This is the same as the default parameter
        g = TextGraph()
        g.index([t.lower() for t in TERMS])
        # Change the preprocess method
        results = g.search('Poimt of sales'.lower(), threshold=0.8, nbest=0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'point of sale')
        self.assertEqual(results[0][1], 2.0)
        path = '[(None), (None), (None), (replace[m -> n], 1), (None), (None), (None), (None), (None), (None), ' \
               '(None), (None), (None), (insert[s], 1), (Final)]'
        self.assertEqual(str(results[0][2]), path)

        # To use upper case instead lower case
        g = TextGraph()
        g.index([t.upper() for t in TERMS])
        # Change the preprocess method
        results = g.search('Poimt of sales'.upper(), threshold=0.8, nbest=0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'POINT OF SALE')
        self.assertEqual(results[0][1], 2.0)
        path = '[(None), (None), (None), (replace[M -> N], 1), (None), (None), (None), (None), (None), (None), ' \
               '(None), (None), (None), (insert[S], 1), (Final)]'
        self.assertEqual(str(results[0][2]), path)

        # Do not use any entity preprocess
        g = TextGraph()
        g.index(TERMS)
        # Change the preprocess method
        results = g.search('Poimt of sales', threshold=0.75, nbest=0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'point of sale')
        self.assertEqual(results[0][1], 3.0)
        path = '[(replace[P -> p], 1), (None), (None), (replace[m -> n], 1), (None), (None), (None), (None), (None), ' \
               '(None), (None), (None), (None), (insert[s], 1), (Final)]'
        self.assertEqual(str(results[0][2]), path)

    def test_entity_levenshtein(self) -> None:
        # I use Graph() instead TextGraph() but with WeightedLevenshtein
        lev = WeightedLevenshtein()
        lev.add_replace_cost("ɛ", "ˈɛ", 0.1)
        lev.add_replace_cost("ˈʊ", "ʊ", 0.1)
        lev.add_replace_cost("aɪ", "ˈaɪ", 0.1)
        g = Graph(distance=lev)
        g.add(["h", "ˈɛ", "l", "əʊ"])
        g.add(["h", "ɛ", "l", "ə", "ʊ"])
        g.add(["ɡ", "ˈʊ", "d", "b", "ˈaɪ"])
        g.add(["p", "ˈɔɪ", "n", "t", " ", "ɒ", "v", " ", "s", "e", "ɪ", "l"])
        g.add(["p", "ˈɔɪ", "n", "t", "ɪ", "ŋ"])

        # Search a variant of "hello"
        term = ["h", "ɛ", "l", "əʊ"]
        results = g.search(term)
        self.assertListEqual(results[0][0], ['h', 'ˈɛ', 'l', 'əʊ'])
        self.assertEqual(results[0][1], 0.1)
        self.assertEqual(str(results[0][2]), '[(None), (replace[ɛ -> ˈɛ], 0.1), (None), (None), (Final)]')

    def test_word_levenshtein(self) -> None:
        lev = WeightedLevenshtein()
        lev.add_delete_cost('of', 0.1)
        lev.add_insert_cost('of', 0.1)
        g = Graph(distance=lev)
        g.add(['point', 'of', 'sales'])
        g.add(['pointing'])
        g.add(['reception', 'desk'])
        results = g.search(['point', 'sales'])
        self.assertListEqual(results[0][0], ['point', 'of', 'sales'])
        self.assertEqual(results[0][1], 0.1)
        self.assertEqual(str(results[0][2]), '[(None), (delete[of], 0.1), (None), (Final)]')


if __name__ == '__main__':
    unittest.main()
