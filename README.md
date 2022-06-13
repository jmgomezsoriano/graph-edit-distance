# graph-edit-distance
A set of edit distance edition methods based on graphs.
These methods allow to calculate the edition cost of an entity (for example a word),
among a big quantity of terms with less computational cost than the usual methods.

At the moment, only a normal Levenshtein algorithm is applied, but it is very easy to add new algorithms thanks to
the project structure.

# How to use

Although you can use all kind of sequences of objects, which are hashable and comparable, with the class
_Graph_, we are going to use the class _TextGraph_ specially suited for text entities.
You can create an edit distance graph with this command:

```python
from grapheditdistance import TextGraph

g = TextGraph()
```

And next to add entities:

```python
# Adding entities individually
g.add('hi')
g.add('hello')
# Adding a sequence of entities
g.index(['hola', 'adiós', 'goodbye', 'punto de venta', 'puerta'])
```

Finally, you can calculate the edition distance of a new word against all those previously added terms:

```python
# Search the term with spelling mistakes "pumto de ventas"
results = g.seq_search('pumto de ventas', threshold=0.8, nbest=0)
# It should return
[(
    'pumto de ventas',
    'punto de venta',
    2.0,
    '[(None), (None), (replace[m -> n], 1), (None), (None), (None), (None), (None), \
    (None), (None), (None), (None), (None), (None), (insert[s], 1), (Final)]'
)]
```
Where the first element of the tuple is the original entity, the second the found one, 
the third the edition distance weight, and the last the list of edition operation applied to change the original query
for obtaining the previously indexed one. This method will only return the entities which edition distance is less
than the given threshold of 0.8 respect to the length of the original entity. That means, if the original entity
has 15 character, the maximum number of errors is 3 (len(entity) * (1 - threshold)).

At the moment, the method _search()_ is not implemented yet. this algorith