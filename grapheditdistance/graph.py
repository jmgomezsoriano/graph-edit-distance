from typing import Iterable, Union, Sequence, Hashable, List, Tuple
import networkx as nx
from multiprocessing import cpu_count

from mysutils.method import synchronized
from networkx.classes.reportviews import NodeView

from grapheditdistance import INIT_NODE, FINAL_NODE
from grapheditdistance.base import BaseGraph, NEIGHBORS, VALUE
from multivaluedbtree import MultivaluedBTree
from grapheditdistance.distances import EditDistance, Levenshtein
import matplotlib.pyplot as plt

from grapheditdistance.operators import Operator


class Graph(BaseGraph):
    """ A graph specially suited to calculate edition distances. """
    @property
    def nodes(self) -> NodeView:
        """
        :return: The graph nodes.
        """
        return self._g.nodes

    def __init__(self, distance: EditDistance = Levenshtein(), processors: int = 0) -> None:
        """ Constructor of this edition distance graph.

        :param distance: The algorithm to obtain the operators to apply in each node.
        :param processors: The limit of CPU processors to use in a parallel search.
        """
        # Create the empty graph and add the init and end node
        self._g = nx.MultiDiGraph()
        self._g.add_node(INIT_NODE, **{NEIGHBORS: {}})
        self._g.add_node(FINAL_NODE, **{NEIGHBORS: {}})
        # Set the rest of the object attributes
        self._processors = processors if processors else cpu_count()
        self.distance = distance
        self._entities = {}

    def _add_node(self, value: Hashable, prev_node: int, pos: int, entity: Sequence) -> int:
        """ Create a node and create the edge from the previous node.
           If the previous node already has a neighbor with that value, reuse it.

        :param value: The value of the new node.
        :param prev_node: The previous node id.
        :param pos: The current position in the entity.
        :param entity: The entity that is adding.
        :return: The id of new node or the reuse one.
        """
        neighbors = self.neighbors(prev_node)
        if value in neighbors:
            node = neighbors[value]
        else:
            node = self.__create_node(value, prev_node)
            self._add_edge(prev_node, node, pos, entity)
        return node

    def __next_node_id(self) -> int:
        """ Calculate a new node id.
        :return: A unique node id.
        """
        return len(self._g) - 1

    @synchronized
    def __create_node(self, value: Hashable, prev_node: int) -> int:
        """ Create a new node with a unique id.

        :param value: The value of the node.
        :param prev_node: The previous node.
        :return: The id of the created node.
        """
        node = self.__next_node_id()
        self._g.add_node(node, **{VALUE: value, NEIGHBORS: {}})
        self.set_neighbor(prev_node, node, value)
        return node

    def _add_edge(self, prev_node: int, next_node: int, pos: int, entity: Sequence) -> None:
        """ Add an edge in the graph.

        :param prev_node: The previous node from the edge comes.
        :param next_node: The next node where the edge goes.
        :param pos: The current position in the entity.
        :param entity: The entity that is adding.
        """
        prev_value = entity[pos - 1] if pos > 0 else INIT_NODE
        curr_value = entity[pos] if pos < len(entity) else FINAL_NODE
        for key, weight in self.distance.weights(prev_value, curr_value, pos, entity):
            self._g.add_edge(prev_node, next_node, key=key, weight=weight)

    def add(self, entity: Sequence[Hashable]) -> None:
        """  Add to the graph an entity, which each element of the entity will be a node in the graph.

        :param entity: The entity to add.
        """
        if entity:
            processed_entity = self.preprocess(entity)
            self._entities[processed_entity] = entity
            node = INIT_NODE
            for i, c in enumerate(processed_entity):
                node = self._add_node(c, node, i, processed_entity)
            self._add_edge(node, FINAL_NODE, len(processed_entity), processed_entity)

    def draw(self, edge_labels: bool = False) -> None:
        """  Draw this graph.

        :param edge_labels: True if the edge labels is shown, otherwise False.
        """
        node_labels = {x: self.value(x) for x in self.nodes}
        node_labels = {x: x.replace('_', '') if x in ['_^_', '_$_'] else x for x in node_labels}
        pos = nx.spring_layout(self._g)
        nx.draw(self._g, pos, with_labels=True, labels=node_labels, font_color='white')
        if edge_labels:
            nx.draw_networkx_edge_labels(self._g, pos, edge_labels=self.__edge_labels(), font_color='red')
        plt.plot()

    def __edge_labels(self) -> dict:
        """ Generate a dict that represents the edge labels.

        :return: A dict with the edge label representation.
        """
        edge_labels = {}
        for u_node, v_node, att in self._g.edges:
            atts = edge_labels[(u_node, v_node)] if (u_node, v_node) in edge_labels else []
            atts.append(self._g.edges[u_node, v_node, att]['weight'])
            edge_labels[(u_node, v_node)] = atts
        return edge_labels

    def adjacent(self, node: int) -> Iterable[int]:
        """ An id list of adjacent nodes.

        :param node: The current node.
        :return: A list of integers with the list of adjacent node ids.
        """
        return self._g[node]

    def value(self, node: int) -> Hashable:
        """ A node value.

        :param node: The node to get its value.
        :return: The value that represents the node.
        """
        return self.nodes[node].get('value', '_^_' if node == INIT_NODE else '_$_')

    def seq_search(self, entity: Sequence[Hashable], threshold: float = 0.8, nbest: int = 1) -> List[tuple]:
        """ Sequential search.

        :param entity: The entity to search.
        :param threshold: The edit distance threshold with respect to the length of the entity.
        :param nbest: The number of best results. If 0, then return all the results that exceed the threshold.
        :return: A list of tuples with the original entity, the found entity, the edition distance value,
           and the list of applied operators.
        """
        paths = MultivaluedBTree()
        visited_paths = {}
        # Each tuple has the entity to search, the current position in the entity,
        # the current node, the path to arrive here, and the used operators.
        entity = self.preprocess(entity)
        paths[0.] = (entity, 0, INIT_NODE, [], [])
        limit = len(entity) * (1 - threshold)
        results = []
        # While I have paths to explore
        while len(paths):
            # Get the parameter of the next path to explore with the less edition distance weight
            weight, (entity, pos, node, path, operators) = paths.popitem()
            path_hash = hash(tuple(operators))
            if path_hash not in visited_paths:
                visited_paths[path_hash] = operators
                # Explore that path and get the next path I can explore
                next_paths = self._explore_node(weight, entity, pos, node, path, operators)
                for weight, entity, pos, node, path, operators in next_paths:
                    # If the final node was archived and all the entity was explored, then add it to the result.
                    if node == FINAL_NODE and pos == len(entity):
                        similar_entity = self._resolve_path(path)
                        results.append((entity, self._entities.get(similar_entity, similar_entity), weight, operators))
                    # Otherwise, add the path if its weight is less than the limited by the threshold
                    elif weight <= limit:
                        paths[weight] = (entity, pos, node, path, operators)
                    # If nbest is different to 0, and I've achieved the maximum number of results, return the results.
                    if nbest and len(results) == nbest:
                        return results
        return results

    def search(self, entity: Sequence[Hashable], threshold: float = 0.8, nbest: int = 1) -> List[tuple]:
        """ A parallel search.

        :param entity: The entity to search.
        :param threshold: The edit distance threshold with respect to the length of the entity.
        :param nbest: The number of best results. If 0, then return all the results that exceed the threshold.
        :return: A list of tuples with the original entity, the found entity, the edition distance value,
           and the list of applied operators.
        """
        # TODO: Parallel search with processes.
        raise NotImplemented('This method is not implemented yet. It will in future versions of this module,')
        paths = MultivaluedBTree()
        visited_paths = {}
        # Each tuple has the entity to search, the current position in the entity,
        # the current node, the path to arrive here, and the used operators.
        entity = self.preprocess(entity)
        paths[0.] = (entity, 0, INIT_NODE, [], [])
        limit = len(entity) * (1 - threshold)
        results = []
        # While I have paths to explore
        while len(paths):
            # Get the parameter of the next path to explore with the less edition distance weight
            weight, (entity, pos, node, path, operators) = paths.popitem()
            path_hash = hash(tuple(operators))
            if path_hash not in visited_paths:
                visited_paths[path_hash] = operators
                self._execute_node(weight, entity, pos, node, path, operators)
                # Explore that path and get the next path I can explore
                next_paths = self._explore_node(weight, entity, pos, node, path, operators)
                for weight, entity, pos, node, path, operators in next_paths:
                    # If the final node was archived and all the entity was explored, then add it to the result.
                    if node == FINAL_NODE and pos == len(entity):
                        similar_entity = self._resolve_path(path)
                        results.append((entity, self._entities.get(similar_entity, similar_entity), weight, operators))
                    # Otherwise, add the path if its weight is less than the limited by the threshold
                    elif weight <= limit:
                        paths[weight] = (entity, pos, node, path, operators)
                    # If nbest is different to 0, and I've achieved the maximum number of results, return the results.
                    if nbest and len(results) == nbest:
                        return results

        return results

    def _explore_node(self,
                      weight: float,
                      entity: Sequence[Hashable],
                      pos: int,
                      node: Union[int, str],
                      path: List[Hashable],
                      operators: List[Operator]) -> List[Tuple[float, Sequence, int, int, list, List[Operator]]]:
        """ Explore the neighbors of a node and return all the possible path to explore.

        :param weight: The path weight at the moment.
        :param entity: The entity to search.
        :param pos: The current position of the entity.
        :param node: The current node to get its neighbors.
        :param path: The current path to arrive at this node.
        :param operators: The list of operators to arrive at this node.
        :return: A list of tuples with the parameters of the path to explore in the future.
           Each tuple contains the new weight, the entity, the new position in the entity, the next node id to explore,
           the path to arrive to that node, and the list of operation to arrive to that node.
        """
        results = []
        for adjacent_node in self.adjacent(node):
            for operator in self.distance.costs(pos, entity, self, node, adjacent_node, operators):
                new_weight = weight + operator.cost
                next_pos = pos + operator.increase_pos
                next_node = operator.next_node
                new_path = path + operator.operate()
                new_operators = operators + [operator]
                results.append((new_weight, entity, next_pos, next_node, new_path, new_operators))
        return results

    def _resolve_path(self, path: List[Hashable]) -> Sequence:
        """  If it is necessary to convert the path to the final user.

        :param path: A list that represents the path.
        :return: A new representation of the path. By default, it returns the same path without changes.
        """
        return path


class TextGraph(Graph):
    """ A special edition distance graph for texts. """
    def __init__(self,
                 case_insensitive: bool = True,
                 distance: EditDistance = Levenshtein(),
                 processors: int = 0) -> None:
        """ Constructor of this text edition distance graph.

        :param case_insensitive: True if convert the entities in lowercase.
        :param distance: The algorithm to obtain the operators to apply in each node.
        :param processors: The limit of CPU processors to use in a parallel search.
        """
        super().__init__(distance, processors)
        self.case_insensitive = case_insensitive

    def preprocess(self, entity: str) -> str:
        """ Convert an entity to lowercase.

        :param entity: The entity to convert.
        :return: A lowercase entity.
        """
        return entity.lower() if self.case_insensitive else entity

    def _resolve_path(self, path: List[Hashable]) -> str:
        """ Convert the list of characters to a string.

        :param path: The path.
        :return: The string that represents that path. In a TextGraph, this represents the string with the found entity.
        """
        return ''.join(super(TextGraph, self)._resolve_path(path))
