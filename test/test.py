import multiprocessing
import pickle

from multivaluedbtree import MultivaluedBTree
from BTrees.OOBTree import OOBTree


class MyClass(OOBTree):
    def __init__(self, lock=None):
        self._a:int = 1
        self.b:str = 'a'
        self.c:list = []
        self.d:dict = {}
        self._lock = lock

    def adquire(self):
        with self._lock:
            print('Prueba adquiriendo el lock en el namespace')


def test():
    MyClass()
    # Crear un Manager
    manager = multiprocessing.Manager()

    # Obtener el espacio de nombres compartido
    namespace = manager.Namespace()

    # Agregar algunos atributos al espacio de nombres
    namespace.variable1 = "valor1"
    namespace.variable2 = "valor2"
    tree = MyClass(manager.Lock())
    namespace.tree = tree

    print(tree.__dict__)
    print(namespace.tree.__dict__)

    # Acceder a los atributos del espacio de nombres
    print(namespace.variable1)
    print(namespace.variable2)

    tree.adquire()

    tree = OOBTree()
    tree['a'] = [1, 2, 3]
    with open('file.pkl', 'wb') as file:
        pickle.dump(tree, file)

    with open('file.pkl', 'rb') as file:
        tree = pickle.load(file)
    print(tree['a'])




if __name__ == '__main__':
    test()
