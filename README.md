# graph-edit-distance
A set of edit distance edition methods based on graphs.
These methods allow to calculate the edition cost of an entity (for example a word),
among a big quantity of terms with less computational cost than the usual methods.

At the moment, only a normal Levenshtein algorithm is applied, but it is very easy to add new algorithms thanks to
the project structure.

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

from grapheditdistance.preprocess import dummy_preprocess
# Do not use any entity preprocess
g = TextGraph(preprocess=dummy_preprocess)
g.index(TERMS)
# Change the preprocess method
results = g.search('Poimt of sales', threshold=0.75, nbest=0, )
print(results)
```