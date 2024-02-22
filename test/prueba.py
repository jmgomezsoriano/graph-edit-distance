import multiprocessing
import pickle
import enum
from enum import unique
from typing import Tuple, List, Any

from multiprocessing import Lock


@unique
class QueueType(enum.Enum):
    """ Enumeration with the available queue types. """
    LIFO = 1
    FIFO = 2

# ARBOL ORDENADO
class ArbolOrdenado:
    def __init__(self):
        self.arbol = {1:[1,2,3]}

    def insertar(self, clave, valor):
        if clave not in self.arbol:
            self.arbol[clave] = []
        self.arbol[clave].append(valor)
        self.arbol = sorted(self.arbol.items())

    def imprimir(self):
        for clave, valores in self.arbol.items():
            print(f"Clave: {clave}, Valores: {valores}")

    def minKey(self):
        if not self.arbol:
            raise KeyError("El árbol está vacío")
        return next(iter(self.arbol))

    def maxKey(self):
        if not self.arbol:
            raise KeyError("El árbol está vacío")
        return next(reversed(self.arbol))

    def get(self, key, default=None):
        return self.arbol.get(key, default)


# CLASE MULTIVALUEDBTREE DE GRAPH.PY
class MultivaluedBTree(ArbolOrdenado):

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

    def pop(self, key: Any, default: Any = None) -> Any:
        """ Extract one element of the key. If the key does not exist or return the default if it is defined,
           otherwise raise KeyError exception.

        :param key: The key.
        :param default: The default value, if it is not given, an exception is raise if the key does not exist.
        :return: The first element ot extract of that key.
           You can change this order with the queue_type parameter of the class constructor.
        """
        self._lock.acquire()
        try:
            return self.__pop(key, default)
        finally:
            self._lock.release()

    def popitem(self) -> Tuple[object, object]:
        """ Extract a tuple with the key and key value of the first key and first key value.
           The order of the keys and the key values can be changed with the constructor parameters
           "reverse" and "queue_type", respectively.

        :return: A tuple with the first key and the first key value.
        """
        self._lock.acquire()
        try:
            key = self.maxKey() if self._reverse else self.minKey()
            value = self.__pop(key)
            return key, value
        finally:
            self._lock.release()

    def __pop(self, key: Any, default: Any = None) -> Any:
        """ Extract one element of the key. If the key does not exist or return the default if it is defined,
           otherwise raise KeyError exception. This method is not process synchronized.

        :param key: The key.
        :param default: The default value, if it is not given, an exception is raise if the key does not exist.
        :return: The first element ot extract of that key.
           You can change this order with the queue_type parameter of the class constructor.
        """
        values = self[key] if default is None else self.get(key, [default])
        value = values.pop()
        if not values and key in self:
            del self[key]
        self._length -= 1
        return value

    def __delete__(self, instance: object) -> None:
        """ Delete an instance of this BTree, even if the key has assigned several values.

        :param instance: The key to delete.
        """
        self._lock.acquire()
        try:
            self._length -= len(self[instance])
            del self[instance]
        finally:
            self._lock.release()

    def __setitem__(self, key: object, value: object) -> None:
        """ Assign or add a value to that key.
        :param key: The key.
        :param value: The value to assign or add to that key.
        """
        self._lock.acquire()
        try:
            values = self[key] if key in self else []
            if self._queue_type == QueueType.LIFO:
                values.append(value)
            else:
                values.insert(0, value)
            super().__setitem__(key, values)
            self._length += 1
        finally:
            self._lock.release()

    def __len__(self) -> int:
        """
        :return: The number of values of this tree.
        """
        return self._length

    def __repr__(self):
        """
        :return: A representation of this object.
        """
        return repr(self.to_dict())

    def to_dict(self) -> dict:
        """
        :return: A dictionary representation of this tree.
        """
        return {key: values for key, values in self.items()}

    def values(self, minimum: object = None, maximum: object = None) -> List[object]:
        """
        values([minimum, maximum]) -> list of values which the key is >= minimum and <= maximum.

        Returns the values of the BTree.  If min and max are supplied, only
        values corresponding to keys greater than min and less than max are
        returned.
        """
        results = []
        for values in super().values(minimum, maximum):
            results.extend(values)
        if self._reverse:
            results.reverse()
        return results

    def update(self, collection: dict) -> None:
        """ Update this collection with other in dictionary format.
        :param collection: The other collection.
        """
        for key, value in collection.items():
            if isinstance(collection, MultivaluedBTree):
                for v in value:
                    self[key] = v
            else:
                self[key] = value

    def adquire(self):
        with self._lock:
            print('Prueba adquiriendo el lock en el namespace')


def test():
    # Crear un Manager
    manager = multiprocessing.Manager()

    # Obtener el espacio de nombres compartido
    namespace = manager.Namespace()

    # Agregar algunos atributos al espacio de nombres
    namespace.variable1 = "valor1"
    namespace.variable2 = "valor2"

    tree = MultivaluedBTree(lock=manager.Lock())
    print(tree.__dict__)
    namespace.tree = tree
    print(namespace.tree.__dict__)

    # Acceder a los atributos del espacio de nombres
    print(namespace.variable1)
    print(namespace.variable2)

    tree.adquire()

    tree = MultivaluedBTree(lock=manager.Lock())
    clave, valor = tree.popitem()
    print(clave, valor)

    with open('file.pkl', 'wb') as file:
        pickle.dump(tree, file)

    with open('file.pkl', 'rb') as file:
        tree = pickle.load(file)


if __name__ == '__main__':
    test()