import unittest

from grapheditdistance.graph import TextGraph


class MyTestCase(unittest.TestCase):
    def test_create_text_graph(self) -> None:
        g = TextGraph()
        g.add('Hello')
        g.add('Goodbye')
        g.add('Saturday')
        g.add('Saturdays')
        g.draw()
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
