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

    def insert(self, key, value, left=None, right=None):
        if not self.root:
            self.nodes[key] = {'value': value, 'left': left, 'right': right}
            self.root.append(key)
        else:
            self._insert_recursively(self.root, key, value, left, right)

    def _insert_recursively(self, node_key, key, value, left=None, right=None):
        node = self.nodes[node_key[0]]
        if key < node_key[0]:
            if node['left'] is None:
                self.nodes[node_key[0]] = {'value': node['value'], 'left': key, 'right': node['right']}
                self.nodes[key] = {'value': value, 'left': left, 'right': right}
            else:
                self._insert_recursively([node['left']], key, value, left, right)
        else:
            if node['right'] is None:
                self.nodes[node_key[0]] = {'value': node['value'], 'left': node['left'], 'right': key}
                self.nodes[key] = {'value': value, 'left': left, 'right': right}
            else:
                self._insert_recursively([node['right']], key, value, left, right)

    def delete(self, key):
        self._delete_recursive(self.root, key)

    def _delete_recursive(self, node_key, key):
        if not node_key:
            return None

        node = self.nodes[node_key[0]]

        if node_key[0] == key:
            del self.root[0]
        elif node['right'] == key:
            self.nodes[node_key[0]] = {'value': node['value'], 'left': node['left'], 'right': None}
            node = self.nodes[key]
        elif node['left'] == key:
            self.nodes[node_key[0]] = {'value': node['value'], 'left': None, 'right': node['right']}
            node = self.nodes[key]
        elif key < node_key[0]:
            self._delete_recursive([node['left']], key)
            return
        elif key > node_key[0]:
            self._delete_recursive([node['right']], key)
            return
        else:
            raise KeyError(f'The key {key} not found')

        children = node['left'], node['right']
        del self.nodes[key]
        for child in children:
            if child:
                self.insert(child, self.nodes[child]['value'], self.nodes[child]['left'],
                            self.nodes[child]['right'])

        # else:
        #     # Encontrado el nodo a eliminar
        #     # Paso 1: Actualizar el padre
        #     if node == self.root:
        #         self.root = None
        #
        #     else:
        #         parent = self._search_parent_recursively(self.root, key)
        #         padre = self.nodes[parent[0]]
        #         if self.nodes[parent[0]]["left"] == key:
        #             self.nodes[parent[0]] = {'value': padre['value'], 'left': None, 'right': padre['right']}
        #         elif self.nodes[parent[0]]["right"] == key:
        #             self.nodes[parent[0]] = {'value': padre['value'], 'left': padre['left'], 'right': None}
        #
        #     del self.nodes[node_key[0]]
        #     # Paso 2: Comprobar si tiene hijos
        #     # Caso 2.2: Tiene hijos
        #     if node['left']:
        #         # Guardar el hijo izquierdo
        #         left_child = node['left']
        #         # Insertar el hijo izquierdo en el árbol
        #         self.insert(left_child, self.nodes[left_child]['value'], self.nodes[left_child]['left'],
        #                     self.nodes[left_child]['right'])
        #     if node['right']:
        #         # Guardar el hijo derecho
        #         right_child = node['right']
        #         # Insertar el hijo derecho en el árbol
        #         self.insert(right_child, self.nodes[right_child]['value'], self.nodes[right_child]['left'],
        #                     self.nodes[right_child]['right'])

    def keys(self):
        if not self.root:
            return []
        return self._inorder_keys(self.root)

    def _inorder_keys(self, node_key):
        node = self.nodes.get(node_key[0])
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

    # def search_parent(self, key):
    #     return self._search_parent_recursively(self.root, key)
    #
    # def _search_parent_recursively(self, node_key, key):
    #     if not node_key:
    #         return None
    #
    #     node = self.nodes[node_key[0]]
    #     if key == node_key[0]:
    #         return None
    #     if key == node['left'] or key == node['right']:
    #         return node_key
    #     if key < node_key[0]:
    #         return self._search_parent_recursively([node['left']], key)
    #     else:
    #         return self._search_parent_recursively([node['right']], key)

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
        min_value = self.nodes[min_key]  # Obtener el valor asociado a la clave mínima
        self.delete(min_key)  # Eliminar la clave mínima del árbol
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
    # print("Minimum Key:", shared_tree.min_key())
    # print("Maximum Key:", shared_tree.max_key())
    print("Keys:", shared_tree.keys())
    # shared_tree[10] = (2, [], "hola")
    # print("Keys after set:", shared_tree.keys())
    # print("Shared BinaryTree keys:", [(key, (value['value'], value['left'], value['right']))
    #                                   for key, value in shared_tree.nodes.items()])
    # print("Minimum Value:", shared_tree.min_value())
    # print("Get key 5 value:", shared_tree.__getitem__(5))
    # print("Get key 10 value:", shared_tree.__getitem__(10))
    del shared_tree[1]
    print("Shared BinaryTree keys after del:", [(key, (value['value'], value['left'], value['right']))
                                                for key, value in shared_tree.nodes.items()])
    print("Keys after del:", shared_tree.keys())
    key, value = shared_tree.popitem()
    print("Trying popitem method:", key, value)
    print("Keys after popitem:", shared_tree.keys())
    print("Shared BinaryTree keys after popitem:", [(key, (value['value'], value['left'], value['right']))
                                                    for key, value in shared_tree.nodes.items()])
