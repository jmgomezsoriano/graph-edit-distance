# graph-edit-distance
A set of edit distance edition methods based on graphs.
These methods allow to calculate the edition cost of an entity (for example a word),
among a big quantity of terms with less computational cost than the usual methods.

At the moment, only a normal Levenshtein algorithm is applied, but it is very easy to add new algorithms thanks to
the project structure.

# Important note

The preprocess parameter in _Graph()_ constructor is not being available in further versions, don't use it, please.

# Install

```bash
pip install grapheditdistance
```

# How to use

Although you can use all type of sequences of objects, which are hashable and comparable, with the class
_Graph_, we are going to use the class _TextGraph_ specially suited for text entities.
You can create an edit distance graph with this command:

```python
from grapheditdistance import TextGraph

g = TextGraph()
```

And next to add entities by two different methods: _add()__ to add just one entity,
and _index()_ to add multiple entities at once.

```python
# Adding entities individually
g.add('hi')
g.add('hello')
# Adding a sequence of entities
g.index(['bye', 'goodbye', 'point of sale', 'pointing'])
```

Finally, you can calculate the edition distance of a new word against all those previously added terms:

```python
# Search the term with spelling mistakes "Poimt of sales"
results = g.search('Poimt of sales', threshold=0.8, nbest=0)
# It should return
[(
    'poimt of sales',
    'point of sale',
    2.0,
    '[(None), (None), (None), (replace[m -> n], 1), (None), (None), (None), (None), (None), (None), \
    (None), (None), (None), (insert[s], 1), (Final)]'
)]
```
Where the first element of the tuple is the preprocessed entity, the second is the found entity, 
the third is the edition distance weight, and the last the list of edition operation applied to change the 
preprocessed query for obtaining the previously indexed one.
This method will only return the entities which edition distance is less
than the given threshold of 0.8 respect to the length of the original entity. That means, if the original entity
has 15 character, the maximum number of errors is 3 (len(entity) * (1 - threshold)). You can limit the number of best
results with the parameter _nbest_, 0 for no limit.

By default, _TextGraph_ uses _str.lower()_ to preprocess the entity. However, you can change the preprocess function
with the parameter _preprocess_:

```python
from grapheditdistance import TextGraph

TERMS = ['hello', 'bye', 'goodbye', 'point of sale', 'pointing']

# This is the same as the default parameter
g = TextGraph(preprocess=str.lower)
g.index(TERMS)
# Change the preprocess method
results = g.search('Poimt of sales', threshold=0.8, nbest=0)
print(results)

# To use upper case instead lower case
g = TextGraph(preprocess=str.upper)
g.index(TERMS)
# Change the preprocess method
results = g.search('Poimt of sales', threshold=0.8, nbest=0)
print(results)

# Do not use any entity preprocess
g = TextGraph(preprocess=None)
g.index(TERMS)
# Change the preprocess method
results = g.search('Poimt of sales', threshold=0.75, nbest=0, )
print(results)
```

# Changing the edit distance algorithm

You can easily to change the edit distance algorithm by the parameter _distance_.
For example, instead of using the basic Levenshtein algorithm, you can use the weighted one, which that, 
you can define different weights for specific operation with given entity elements:

```python
from grapheditdistance import TextGraph
from grapheditdistance.distances import WeightedLevenshtein

TERMS = ['hello', 'bye', 'goodbye', 'point of sale', 'pointing']

lev = WeightedLevenshtein()
lev.add_insert_cost(' ', 0.1)
lev.add_delete_cost(' ', 0.1)
lev.add_replace_cost(' ', '-', 0.1)
lev.add_replace_cost('-', ' ', 0.1)
tree = TextGraph(distance=lev)
tree.index(TERMS)
results = tree.search('Poi ntof-sales', nbest=1)
print(results)
```

# Defining your own edit distance algorithm

In order to define you own algorithm, you only need to create a class from the super class _EditDistance_.
For example:

```python
from grapheditdistance.graph import BaseGraph
from grapheditdistance.operators import Operator
from grapheditdistance.distances import EditDistance
from typing import List, Sequence, Hashable

class MyEditDistanceAlgorithm(EditDistance):
    def max_cost(self) -> float:
        """
        :return: The maximum cost.
        """
        float_value = ...
        return float_value # The maximum possible cost.

    def costs(self,
              pos: int,
              entity: Sequence[Hashable],
              graph: BaseGraph,
              curr_node: int,
              next_node: int,
              operators: List[Operator]) -> List[Operator]:
        list_operators = ...
        return list_operators  # A new list of operators to arrive to next node. 
```

Where _pos_ is the current position of the entity that we are evaluating; _entity_ is the entity to compare with,
the _graph_ with all the system entities to compare against; _curr_node_ is the current node in the graph;
_next_node_ is the next node we want to jump;
_operators_ are the list of operators to arrive to the current node.

The result should be the new operators to explore. For example, if to pass from node X to node Y we need to
remove the character A, or to add the character B, or replace A by B, we need to return a list of three operators:
[_DeleteOperator(A)_, _InsertOperator(B)_, _ReplaceOperator(A, B)_]. You can also add the operator _NoneOperator()_ to
indicate that passing from node X to Y does not require any costly operation, or _FinalOperator()_ to indicate that
we have already achieved the final node.

The available operators are in the package _grapheditdistance.operator_, however, you can define your own operators
by inheriting from the class _grapheditdistance.operator.Operator_.

# Other examples of use

At the moment, we have shown text edit distance examples. But, this algorithm can be used with other elements.
For example, to use it with phonetic distance problems. For example:

```python
from grapheditdistance import Graph
from grapheditdistance.distances import WeightedLevenshtein

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
print(g.search(term))
# Prints: [(['h', 'ɛ', 'l', 'əʊ'], ['h', 'ˈɛ', 'l', 'əʊ'], 0.1, [(None), (replace[ɛ -> ˈɛ], 0.1), (None), (None), (Final)])]
```
