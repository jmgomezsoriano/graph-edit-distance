import multiprocessing


class Node:
    @property
    def key(self):
        return self._namespace.key

    @key.setter
    def key(self, key):
        self._namespace.key = key

    @property
    def value(self):
        return self._namespace.value

    @value.setter
    def value(self, value):
        self._namespace.value = value

    @property
    def left(self):
        return self._namespace.left

    @left.setter
    def left(self, node):
        self._namespace.left = node

    @property
    def right(self):
        return self._namespace.right

    @right.setter
    def right(self, node):
        self._namespace.right = node

    def __init__(self, key, value):
        self._namespace = multiprocessing.Manager().Namespace()
        self._namespace.key = key
        self._namespace.value = value
        self._namespace.left = None
        self._namespace.right = None


class BinaryTree:
    def __init__(self):
        manager = multiprocessing.Manager()
        self.nodes = manager.dict()
        self.root = manager.list()

    def insert(self, key, value):
        if not self.root:
            self.nodes[key] = {'value': value, 'left': None, 'right': None}
            self.root.append(key)
        else:
            self._insert_recursively(self.root, key, value)

    def _insert_recursively(self, node_key, key, value):
        node = self.nodes[node_key[0]]
        if key < node_key[0]:
            if node['left'] is None:
                self.nodes[node_key[0]] = {'value': node['value'], 'left': key, 'right': node['right']}
                self.nodes[key] = {'value': value, 'left': None, 'right': None}
            else:
                self._insert_recursively([node['left']], key, value)
        else:
            if node['right'] is None:
                self.nodes[node_key[0]] = {'value': node['value'], 'left': node['left'], 'right': key}
                self.nodes[key] = {'value': value, 'left': None, 'right': None}
            else:
                self._insert_recursively([node['right']], key, value)

    def delete(self, key):
        if not self.root:
            raise KeyError("BinaryTree is empty")
        self.root[0] = self._delete_recursively(self.root[0], key)

    def _delete_recursively(self, node_key, key):
        if not node_key:
            return None
        node = self.nodes[node_key]
        if key == node_key:
            if node['left'] is None and node['right'] is None:
                del self.nodes[node_key]
                return None
            elif node['left'] is None:
                right_child = node['right']
                del self.nodes[node_key]
                return right_child
            elif node['right'] is None:
                left_child = node['left']
                del self.nodes[node_key]
                return left_child
            else:
                successor_key = self._min_key_recursively(node['right'])
                successor_value = self.nodes[successor_key]['value']
                self._delete_recursively(node['right'], successor_key)
                node['key'] = successor_key
                node['value'] = successor_value
                return node_key
        elif key < node_key:
            node['left'] = self._delete_recursively(node['left'], key)
        else:
            node['right'] = self._delete_recursively(node['right'], key)
        return node_key

    def keys(self):
        if not self.root:
            return []
        return self._inorder_keys(self.root)

    def _inorder_keys(self, node_key):
        node = self.nodes.get(node_key[0])  # Utiliza .get() para evitar errores de KeyError
        if not node:
            return []

        keys = []
        if node['left'] is not None:
            keys.extend(self._inorder_keys([node['left']]))
        keys.append(node_key[0])
        if node['right'] is not None:
            keys.extend(self._inorder_keys([node['right']]))
        return keys

    def min_key(self):
        if not self.root:
            raise ValueError("BinaryTree is empty")
        return self._min_key_recursively(self.root[0])

    def _min_key_recursively(self, node_key):
        node = self.nodes[node_key]
        if node['left'] is None:
            return node_key
        return self._min_key_recursively(node['left'])

    def max_key(self):
        if not self.root:
            raise ValueError("BinaryTree is empty")
        return self._max_key_recursively(self.root[0])

    def _max_key_recursively(self, node_key):
        node = self.nodes[node_key]
        if node['right'] is None:
            return node_key
        return self._max_key_recursively(node['right'])

    def search(self, key):
        return self._search_recursively(self.root, key)

    def _search_recursively(self, node_key, key):
        if not node_key:
            return None
        node = self.nodes[node_key[0]]
        if key == node_key[0]:
            return Node(node_key[0], node['value'])
        elif key < node_key[0]:
            return self._search_recursively([node['left']], key)
        else:
            return self._search_recursively([node['right']], key)

    def min_value(self):
        if not self.root:
            raise ValueError("BinaryTree is empty")
        return self._min_value_recursively(self.root[0])

    def _min_value_recursively(self, node_key):
        node = self.nodes[node_key]
        if node['left'] is None:
            return node['value']
        return self._min_value_recursively(node['left'])

    def popitem(self):
        if not self.root:
            raise KeyError("BinaryTree is empty")

        min_key = self.min_key()  # Obtener la clave mínima
        min_value = self[min_key]  # Obtener el valor asociado a la clave mínima
        del self[min_key]  # Eliminar la clave mínima del árbol
        return min_key, min_value

    def __getitem__(self, key):
        node = self.search(key)
        if node:
            return node.value
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.insert(key, value)

    def __delitem__(self, key):
        self.delete(key)


def process_func(shared_tree, i):
    shared_tree[2 + (i * 3)] = 'A' * (i + 1)
    shared_tree[1 + (i * 3)] = 'B' * (i + 1)
    shared_tree[3 + (i * 3)] = 'C' * (i + 1)


if __name__ == '__main__':
    shared_tree = BinaryTree()

    processes = [multiprocessing.Process(target=process_func, args=(shared_tree, i)) for i in range(2)]

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    # print(shared_tree.root[0], shared_tree.nodes[shared_tree.root[0]]['value'],
    #       shared_tree.nodes[shared_tree.root[0]]['left'], shared_tree.nodes[shared_tree.root[0]]['right'])
    print("Shared BinaryTree keys:", [(key, (value['value'], value['left'], value['right']))
                                      for key, value in shared_tree.nodes.items()])
    print("Minimum Key:", shared_tree.min_key())
    print("Maximum Key:", shared_tree.max_key())
    print("Keys:", shared_tree.keys())
    shared_tree.__setitem__(10, (2, [], "hola"))
    print("Keys after set:", shared_tree.keys())
    # print("Shared BinaryTree keys:", [(key, (value['value'], value['left'], value['right']))
    #                                   for key, value in shared_tree.nodes.items()])
    print("Minimum Value:", shared_tree.min_value())
    # print("Get key 5 value:", shared_tree.__getitem__(5))
    print("Get key 10 value:", shared_tree.__getitem__(10))
    shared_tree.__delitem__(1)
    print("Shared BinaryTree keys after delitem:", [(key, (value['value'], value['left'], value['right']))
                                                    for key, value in shared_tree.nodes.items()])
    print("Keys after del:", shared_tree.keys())
    #key, value = shared_tree.popitem()
    #print("Trying popitem method:", key, value)
