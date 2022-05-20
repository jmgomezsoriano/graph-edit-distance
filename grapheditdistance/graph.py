from typing import Iterable, Union, Sequence, Hashable

import networkx as nx

from graphdistance.distances import EditDistance, Levenshtein

INIT_NODE, FINAL_NODE = '_^_', '_$_'
VALUE, NEIGHBORS, WEIGHT = 'value', 'neighbors', 'weight'


class Graph(object):
    @property
    def graph(self) -> nx.Graph:
        return self.g

    def __init__(self, distance: EditDistance = Levenshtein()) -> None:
        self.distance = distance
        # Create the empty graph and add the init and end node
        self.g = nx.MultiDiGraph()
        self.g.add_node(INIT_NODE, **{NEIGHBORS: {}})
        self.g.add_node(FINAL_NODE, **{NEIGHBORS: {}})

    def _add_node(self, value: Hashable, prev_node: Union[int, str], pos: int, entity: Sequence) -> int:
        if value in self.g.nodes[prev_node][NEIGHBORS]:
            node = self.g.nodes[prev_node][NEIGHBORS]
        else:
            node = len(self.g) - 1
            self.g.add_node(node, **{VALUE: value, NEIGHBORS: {}})
            self.g.nodes[prev_node][NEIGHBORS][value] = node
        self._add_edge(prev_node, node, pos, entity)
        return node

    def _add_edge(self, prev_node: Union[str, int], next_node: Union[str, int], pos: int, entity: Sequence):
        prev_value = entity[pos - 1] if pos > 0 else INIT_NODE
        curr_value = entity[pos] if pos < len(entity) else FINAL_NODE
        next_value = entity[pos + 1] if pos < len(entity) - 1 else FINAL_NODE
        for key, weight in self.distance.weights(prev_value, curr_value, next_value, pos, entity):
            self.g.add_edge(prev_node, next_node, key=key, weight=weight)

    def add(self, entity: Sequence[Hashable]) -> None:
        if entity:
            entity = self.preprocess(entity)
            node = INIT_NODE
            for i, c in enumerate(entity):
                node = self._add_node(c, node, i, entity)
            self._add_edge(node, FINAL_NODE, len(entity), entity)

    def preprocess(self, value: Sequence) -> Sequence:
        return value

    def index(self, terms: Iterable[Sequence[Hashable]]) -> None:
        for term in terms:
            self.add(term)

    def draw(self, edge_labels: bool = False) -> None:
        node_labels = {x: self.g.nodes[x][VALUE] if isinstance(x, int) else x.replace('_', '') for x in self.g.nodes}
        pos = nx.spring_layout(self.g)
        nx.draw(self.g, pos, with_labels=True, labels=node_labels, font_color='white')
        if edge_labels:
            nx.draw_networkx_edge_labels(self.g, pos, edge_labels=self.__edge_labels(), font_color='red')

    def __edge_labels(self) -> dict:
        edge_labels = {}
        for u_node, v_node, att in self.g.edges:
            atts = edge_labels[(u_node, v_node)] if (u_node, v_node) in edge_labels else []
            atts.append(self.g.edges[u_node, v_node, att]['weight'])
            edge_labels[(u_node, v_node)] = atts
        return edge_labels

class TextGraph(Graph):
    def __init__(self, case_insensitive: bool = True, distance: EditDistance = Levenshtein()) -> None:
        super().__init__(distance)
        self.case_insensitive = case_insensitive

    def preprocess(self, entity: str) -> str:
        return entity.lower() if self.case_insensitive else entity
