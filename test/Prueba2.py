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

    def search(self, key):
        return self._search_recursively(self.root, key)

    def _search_recursively(self, node, key):
        if node is None or node.key == key:
            return node
        if key < node.key:
            return self._search_recursively(node.left, key)
        return self._search_recursively(node.right, key)

    def delete(self, key):
        self.root = self._delete_recursively(self.root, key)

    def _delete_recursively(self, node, key):
        if node is None:
            return node
        if key < node.key:
            node.left = self._delete_recursively(node.left, key)
        elif key > node.key:
            node.right = self._delete_recursively(node.right, key)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            temp = self._min_value_node(node.right)
            node.key = temp.key
            node.value = temp.value
            node.right = self._delete_recursively(node.right, temp.key)
        return node

    def _min_value_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current

    def keys(self):
        return self._inorder_traversal(self.root, [])

    def _inorder_traversal(self, node, keys):
        if node:
            self._inorder_traversal(node.left, keys)
            keys.append(node.key)
            self._inorder_traversal(node.right, keys)
        return keys

    def min_key(self):
        if self.root is None:
            return None
        return self._min_key_recursively(self.root)

    def _min_key_recursively(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current.key

    def max_key(self):
        if self.root is None:
            return None
        return self._max_key_recursively(self.root)

    def _max_key_recursively(self, node):
        current = node
        while current.right is not None:
            current = current.right
        return current.key

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

    processes = [multiprocessing.Process(target=process_func, args=(shared_tree, i)) for i in range(3)]

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    # for i in range(3):
    #     process_func(shared_tree, i)

    print(shared_tree.root[0], shared_tree.nodes[shared_tree.root[0]]['value'], shared_tree.nodes[shared_tree.root[0]]['left'], shared_tree.nodes[shared_tree.root[0]]['right'])
    print("Shared BinaryTree keys:", [(key, (value['value'], value['left'], value['right'])) for key, value in shared_tree.nodes.items()])
    # print("Minimum Key:", shared_tree.min_key())
    # print("Maximum Key:", shared_tree.max_key())
    # print("Maximum Key:", shared_tree.keys())
