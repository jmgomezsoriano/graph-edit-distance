from abc import ABCMeta, ABC, abstractmethod
from typing import List, Tuple, Sequence, Any, Hashable

from grapheditdistance.base import BaseGraph
from grapheditdistance.operators import Operator


class EditDistance(ABC):
    """
    Abstract class for all edit distance algorithms.
    """
    __metaclass__ = ABCMeta

    def weights(self,
                prev_value: Any,
                curr_value: Any,
                pos: int,
                entity: Sequence[Hashable]) -> List[Tuple[str, float]]:
        """ Return the weights for the graph edges.

        :param prev_value: The previous node value.
        :param curr_value: The current node value.
        :param pos: The current position in the entities.
        :param entity: The entities.
        :return:
        """
        return [('default', 1.)]

    @property
    @abstractmethod
    def max_cost(self) -> float:
        """
        :return: The maximum cost.
        """
        pass

    @abstractmethod
    def costs(self,
              pos: int,
              entity: Sequence[Hashable],
              graph: BaseGraph,
              curr_node: int,
              next_node: int,
              operators: List[Operator]) -> List[Operator]:
        """ This method should return a list of operators with the different costs of each operation.

        :param pos: The current position of the entity.
        :param entity: The entity is a sequence of hashable elements
        :param graph: The graph.
        :param curr_node: The current node.
        :param next_node: The next node.
        :param operators: The list of operators to arrive to the current node.
        :return: The different operators to explore and add to the previous list of operators.
        """
        pass
