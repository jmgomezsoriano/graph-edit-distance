from typing import Iterable, Union, Sequence, Hashable, List, Tuple
import networkx as nx
from multiprocessing import cpu_count, Pool

from mysutils.method import synchronized
from networkx.classes.reportviews import NodeView

from grapheditdistance.base import BaseGraph, NEIGHBORS, VALUE
from grapheditdistance.btree import MultivaluedBTree
from grapheditdistance.distances import EditDistance, Levenshtein
import matplotlib.pyplot as plt

from grapheditdistance.operators import Operator

INIT_NODE, FINAL_NODE = -1, -2


class Graph(BaseGraph):
    @property
    def nodes(self) -> NodeView:
        return self._g.nodes

    def __init__(self, distance: EditDistance = Levenshtein(), processes: int = None) -> None:
        self.distance = distance
        # Create the empty graph and add the init and end node
        self._g = nx.MultiDiGraph()
        self._g.add_node(INIT_NODE, **{NEIGHBORS: {}})
        self._g.add_node(FINAL_NODE, **{NEIGHBORS: {}})
        self._processes = processes if processes else cpu_count()
        self._entities = {}

    def _add_node(self, value: Hashable, prev_node: int, pos: int, entity: Sequence) -> int:
        node = self.get_neighbor(value, prev_node, self.__create_node(value, prev_node))
        self._add_edge(prev_node, node, pos, entity)
        return node

    def __next_node_id(self) -> int:
        return len(self._g) - 1

    @synchronized
    def __create_node(self, value: Hashable, prev_node: int):
        node = self.__next_node_id()
        self._g.add_node(node, **{VALUE: value, NEIGHBORS: {}})
        self.set_neighbor(prev_node, node, value)
        return node

    def _add_edge(self, prev_node: int, next_node: int, pos: int, entity: Sequence):
        prev_value = entity[pos - 1] if pos > 0 else INIT_NODE
        curr_value = entity[pos] if pos < len(entity) else FINAL_NODE
        # next_value = entity[pos + 1] if pos < len(entity) - 1 else FINAL_NODE
        for key, weight in self.distance.weights(prev_value, curr_value, pos, entity):
            self._g.add_edge(prev_node, next_node, key=key, weight=weight)

    def add(self, entity: Sequence[Hashable]) -> None:
        if entity:
            processed_entity = self.preprocess(entity)
            self._entities[processed_entity] = entity
            node = INIT_NODE
            for i, c in enumerate(processed_entity):
                node = self._add_node(c, node, i, processed_entity)
            self._add_edge(node, FINAL_NODE, len(processed_entity), processed_entity)

    def draw(self, edge_labels: bool = False) -> None:
        node_labels = {x: self.value(x) for x in self.nodes}
        node_labels = {x: x.replace('_', '') if x in ['_^_', '_$_'] else x for x in node_labels}
        pos = nx.spring_layout(self._g)
        nx.draw(self._g, pos, with_labels=True, labels=node_labels, font_color='white')
        if edge_labels:
            nx.draw_networkx_edge_labels(self._g, pos, edge_labels=self.__edge_labels(), font_color='red')
        plt.plot()

    def __edge_labels(self) -> dict:
        edge_labels = {}
        for u_node, v_node, att in self._g.edges:
            atts = edge_labels[(u_node, v_node)] if (u_node, v_node) in edge_labels else []
            atts.append(self._g.edges[u_node, v_node, att]['weight'])
            edge_labels[(u_node, v_node)] = atts
        return edge_labels

    # def search(self, entities: Sequence[Hashable], threshold: float, nbest: int = 1) -> List[Sequence[Hashable]]:
    #     paths = MultivaluedBTree()
    #     node = self._g[INIT_NODE]
    #     weight = 0
    #     number_of_processes = 0
    #     with Pool(self._processes) as pool:
    #         for pos, entity in enumerate(entities):
    #             paths[weight] = (entity, pos, node, [node])
    #             while number_of_processes < self._processes:
    #                 pool.apply_async(_search, (entity, ))

    def adjacent(self, node: int) -> Iterable[int]:
        return self._g[node]

    def value(self, node: int) -> Hashable:
        return self.nodes[node].get('value', '_^_' if node == INIT_NODE else '_$_')

    def seq_search(self, entity: Sequence[Hashable], threshold: float = 0.8, nbest: int = 1) -> List[tuple]:
        paths = MultivaluedBTree()
        # Each tuple has the entity to search, the current position in the entity,
        # the current node, the path to arrive here, and the used operators.
        paths[0.] = (entity, 0, INIT_NODE, [], [])
        limit = len(entity) * (1 - threshold)
        results = []
        while len(paths):
            weight, (entity, pos, node, path, operators) = paths.popitem()
            next_paths = self._explore_node(weight, entity, pos, node, path, operators)
            for weight, entity, pos, node, path, operators in next_paths:
                if node == FINAL_NODE and pos == len(entity):
                    similar_entity = self._resolve_path(path)
                    results.append((entity, similar_entity, weight, operators))
                elif weight <= limit: # and pos < len(entity):
                    paths[weight] = (entity, pos, node, path, operators)
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
        results = []
        for adjacent_node in self.adjacent(node):
            if adjacent_node != FINAL_NODE or pos < len(entity):
                for operator in self.distance.costs(pos, entity, self, node, adjacent_node):
                    new_weight = weight + operator.cost
                    next_pos = pos + operator.encrease_pos
                    next_node = operator.next_node
                    new_path = path + operator.operate()
                    new_operators = operators + [operator]
                    results.append((new_weight, entity, next_pos, next_node, new_path, new_operators))
        return results

    def _resolve_path(self, path: List[int]) -> Sequence:
        return [element for element in path if element not in ['_^_', '_$_']]


class TextGraph(Graph):
    def __init__(self, case_insensitive: bool = True, distance: EditDistance = Levenshtein()) -> None:
        super().__init__(distance)
        self.case_insensitive = case_insensitive

    def preprocess(self, entity: str) -> str:
        return entity.lower() if self.case_insensitive else entity

    def _resolve_path(self, path: List[int]) -> str:
        return ''.join(super(TextGraph, self)._resolve_path(path))
