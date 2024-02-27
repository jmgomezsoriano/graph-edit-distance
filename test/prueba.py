import multiprocessing
import pickle
import enum
from enum import unique

from sortedcontainers import SortedDict


@unique
class QueueType(enum.Enum):
    """ Enumeration with the available queue types. """
    LIFO = 1
    FIFO = 2


#MULTIVALUEDTREE
class MultivaluedTree(SortedDict):
    def __init__(self, reverse: bool = False, queue_type: QueueType = QueueType.LIFO, lock=None, *args, **kwargs) -> None:
        """ Constructor.
        :param reverse: False if the keys are ordered incrementally, if True, the order is decremental.
        :param queue_type: For each key, how to get the values with pop() and popitem() methods.
            By default, its value is QueueType.LIFO (Last In, First Out),
            but it can be also QueueType.FIFO (First In, First Out).
        :param kwargs: Extra parameters for OOBTree object.
        """
        super().__init__(*args, **kwargs)
        self._queue_type = queue_type
        self._reverse = reverse
        self._lock = lock
        self._length = 0

    def min_key(self):
        """Return the minimum key in the namespace.graph."""
        if not self:
            raise ValueError("Empty namespace.graph")
        return next(iter(self.keys()))

    def max_key(self):
        """Return the maximum key in the namespace.graph."""
        if not self:
            raise ValueError("Empty namespace.graph")
        return next(reversed(self.keys()))

    def __getitem__(self, key):
        """Get item from the namespace.graph by key."""
        if key not in self:
            raise KeyError(f"Key '{key}' not found in namespace.graph")
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        """Set item in the namespace.graph with key and value."""
        if key in self:
            raise ValueError(f"Key '{key}' already exists in namespace.graph")
        super().__setitem__(key, value)

    def popitem(self, index=-1):
        """Remove and return ``(key, value)`` pair at `index` from the namespace.graph."""
        key, value = super().popitem(index)
        return key, value


def test(lock, graph):

    # Crear un grafo ordenado
    graph[2] = ('helado', 0, [])
    graph[0] = 'coche'
    graph[1] = 'casa'
    print(graph.__dict__)

    # Operaciones básicas
    print("Mínima clave:", graph.min_key())
    print("Máxima clave:", graph.max_key())

    # Acceder a un elemento
    print("Valor de '2':", graph[2])

    # Añadir un elemento
    graph[3] = 'valor'
    print("Claves del grafo después de añadir '3':", graph.keys())

    # Eliminar un elemento
    key, value = graph.popitem()
    print("Elemento eliminado:", key, value)

    tree = MultivaluedTree(lock=lock)

    with open('file.pkl', 'wb') as file:
        pickle.dump(tree, file)

    with open('file.pkl', 'rb') as file:
        tree = pickle.load(file)


if __name__ == '__main__':
    manager = multiprocessing.Manager()
    lock = manager.Lock()
    graph = manager.Namespace().graph = MultivaluedTree(lock=lock)

    test(lock, graph)
