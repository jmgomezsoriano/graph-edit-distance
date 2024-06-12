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
        """Return the minimum key in the graph."""
        if not self:
            raise ValueError("Empty graph")
        return next(iter(self.keys()))

    def max_key(self):
        """Return the maximum key in the graph."""
        if not self:
            raise ValueError("Empty graph")
        return next(reversed(self.keys()))

    def __getitem__(self, key):
        """Get item from the graph by key."""
        if key not in self:
            raise KeyError(f"Key '{key}' not found in graph")
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        """Set item in the graph with key and value."""
        if key in self:
            raise ValueError(f"Key '{key}' already exists in graph")
        super().__setitem__(key, value)

    def popitem(self, index=-1):
        """Remove and return ``(key, value)`` pair at `index` from the graph."""
        key, value = super().popitem(index)
        return key, value


def process_task(graph, process_id):
    for i in range(4):
        graph[process_id * 4 + i] = f"value_{process_id}_{i}"
        print(f"Process {process_id}: Added value_{process_id}_{i}")
    print(graph.min_key())


if __name__ == '__main__':
    with multiprocessing.Manager() as manager:
        namespace = manager.Namespace()
        namespace.graph = MultivaluedTree()

        processes = []
        for i in range(1):
            # p = multiprocessing.Process(target=process_task, args=(lock, graph, i))
            p = multiprocessing.Process(target=process_task, args=(namespace.graph, i))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        # print("Final graph:", graph)
        print("Final graph:", namespace.graph.min_key())
