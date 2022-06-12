from typing import Tuple, List

from BTrees.OOBTree import OOBTree
from multiprocessing import Lock


class MultivaluedBTree(OOBTree):
    """ A multivalued implementation of a BTree. That means, a BTree which the value of a (key, value) pair can
    save several values in the same key instead of just one. Therefore, when you execute:

       <code>
       tree = MultivaluedBTree()
       tree['a'] = 1
       tree['a'] = 2
       <code/>

    The second value does not replace the first one, but it store the two. Therefore, if you do the following:
       ```python
       print(tree['a'])
       ```
    The list [1, 2] is printed.
    """
    def __init__(self, decremental_order: bool = False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.decremental_order = decremental_order
        self.lock = Lock()
        self.length = 0

    def popitem(self) -> Tuple[object, object]:
        self.lock.acquire()
        try:
            key = self.maxKey() if self.decremental_order else self.minKey()
            values = self[key]
            value = values.pop()
            if not values:
                del self[key]
            self.length -= 1
            return key, value
        finally:
            self.lock.release()

    def __delete__(self, instance: object) -> None:
        self.lock.acquire()
        try:
            self.length -= len(self[instance])
            del self[instance]
        finally:
            self.lock.release()

    def __setitem__(self, key: object, value: object) -> None:
        self.lock.acquire()
        try:
            values = self[key] if key in self else []
            values.append(value)
            super().__setitem__(key, values)
            self.length += 1
        finally:
            self.lock.release()

    def __len__(self) -> int:
        return self.length

    def __repr__(self):
        return repr({key: values for key, values in self.items()})
    # def values(self, min: object = None, max: object = None) -> List[object]:
    #     """
    #     values([min, max]) -> list of values
    #
    #     Returns the values of the BTree.  If min and max are supplied, only
    #     values corresponding to keys greater than min and less than max are
    #     returned.
    #     """
    #     pass
    #
    # def nbest(self, num: int) -> List[object]:
    #     """
    #
    #     :param num:
    #     :return:
    #     """
    #     passlen