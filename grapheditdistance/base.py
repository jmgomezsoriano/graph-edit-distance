from abc import ABC, ABCMeta, abstractmethod
from typing import Hashable, Sequence, Iterable, List

from networkx.classes.reportviews import NodeView

VALUE, NEIGHBORS, WEIGHT = 'value', 'neighbors', 'weight'


class BaseGraph(ABC):
    """ An abstract graph. """
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def nodes(self) -> NodeView:
        """
        :return: The graph nodes.
        """
        pass

    def neighbors(self, node: int) -> dict:
        """ The following neighbors of that node.
        :param node: The node id.
        :return: A dictionary with the neighbors.
        """
        return self.nodes[node][NEIGHBORS]

    def get_neighbor(self, value: Hashable, node: int, default: int = None) -> int:
        """ Get a given neighbor with a given value.

        :param value: The value to search.
        :param node: The node to search the neighbor
        :param default: The default value if the value is not in the node neighbors.
        :return: The neighbor node id.
        """
        return self.neighbors(node).get(value, default)

    def set_neighbor(self, prev_node: int, node: int, value: Hashable) -> None:
        """ Set a neighbor to this node.

        :param prev_node: The previous node.
        :param node: The current node.
        :param value: The value of the node.
        """
        self.neighbors(prev_node)[value] = node

    @abstractmethod
    def add(self, entity: Sequence[Hashable]) -> None:
        """  Add to the graph an entity, which each element of the entity will be a node in the graph.

        :param entity: The entity to add.
        """
        pass

    def preprocess(self, entity: Sequence[Hashable]) -> Sequence[Hashable]:
        """ Preprocess an entity before to add to the graph.
        :param entity: The entity.
        :return:
        """
        return entity

    def index(self, entities: Iterable[Sequence[Hashable]]) -> None:
        """ Index several entities.

        :param entities: Any iterable of entities.
        """
        for entity in entities:
            self.add(entity)

    @abstractmethod
    def draw(self, edge_labels: bool = False) -> None:
        """  Draw this graph.

        :param edge_labels: True if the edge labels is shown, otherwise False.
        """
        pass

    @abstractmethod
    def adjacent(self, node: int) -> Iterable[int]:
        """ An id list of adjacent nodes.

        :param node: The current node.
        :return: A list of integers with the list of adjacent node ids.
        """
        pass

    @abstractmethod
    def value(self, node: int) -> Hashable:
        """ A node value.

        :param node: The node to get its value.
        :return: The value that represents the node.
        """
        pass

    @abstractmethod
    def seq_search(self, entity: Sequence[Hashable], threshold: float = 0.8, nbest: int = 1) -> List[tuple]:
        """ Sequential search.

        :param entity: The entity to search.
        :param threshold: The edit distance threshold with respect to the length of the entity.
        :param nbest: The number of best results. If 0, then return all the results that exceed the threshold.
        :return: A list of tuples with the original entity, the found entity, the edition distance value,
           and the list of applied operators.
        """
        pass
